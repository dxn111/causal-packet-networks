"""Small deterministic DAG scheduler for CPN feasibility experiments.

This is a graph-level simulator only. It does not model GPU kernels, batching,
token quality, or language-model inference latency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class Packet:
    name: str
    duration: float
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScheduledPacket:
    name: str
    worker: int
    start: float
    finish: float


@dataclass(frozen=True)
class ScheduleResult:
    packets: tuple[ScheduledPacket, ...]
    work: float
    critical_path: float
    makespan: float
    workers: int

    @property
    def ideal_speedup_bound(self) -> float:
        """Work divided by the best possible makespan on unlimited hardware."""
        if self.critical_path == 0:
            return 1.0
        return self.work / self.critical_path

    @property
    def simulated_speedup(self) -> float:
        """Serial work divided by this simulator's list-scheduled makespan."""
        if self.makespan == 0:
            return 1.0
        return self.work / self.makespan


def _validate_and_index(packets: Sequence[Packet]) -> dict[str, Packet]:
    by_name: dict[str, Packet] = {}
    for packet in packets:
        if packet.name in by_name:
            raise ValueError(f"duplicate packet name: {packet.name}")
        if packet.duration < 0:
            raise ValueError(f"negative duration for packet: {packet.name}")
        by_name[packet.name] = packet

    for packet in packets:
        missing = set(packet.dependencies) - by_name.keys()
        if missing:
            raise ValueError(
                f"packet {packet.name} has unknown dependencies: {sorted(missing)}"
            )
        if packet.name in packet.dependencies:
            raise ValueError(f"packet {packet.name} depends on itself")
    return by_name


def _topological_order(by_name: Mapping[str, Packet]) -> list[str]:
    remaining = {name: set(packet.dependencies) for name, packet in by_name.items()}
    order: list[str] = []
    ready = sorted(name for name, deps in remaining.items() if not deps)

    while ready:
        name = ready.pop(0)
        order.append(name)
        for other in sorted(remaining):
            if name in remaining[other]:
                remaining[other].remove(name)
                if not remaining[other]:
                    ready.append(other)
        ready.sort()

    if len(order) != len(by_name):
        cyclic = sorted(name for name, deps in remaining.items() if deps)
        raise ValueError(f"dependency graph contains a cycle involving: {cyclic}")
    return order


def _critical_path(by_name: Mapping[str, Packet], order: Sequence[str]) -> dict[str, float]:
    successors: dict[str, list[str]] = {name: [] for name in by_name}
    for packet in by_name.values():
        for parent in packet.dependencies:
            successors[parent].append(packet.name)

    tail: dict[str, float] = {}
    for name in reversed(order):
        tail[name] = by_name[name].duration + max(
            (tail[child] for child in successors[name]), default=0.0
        )
    return tail


def schedule_packets(packets: Sequence[Packet], workers: int) -> ScheduleResult:
    """List-schedule a DAG onto identical workers, prioritizing longest tails.

    Dependencies constrain packet start times. The critical-path priority is a
    simple heuristic; real runtimes need measurements for packet costs,
    communication, batching, and hardware-specific scheduling.
    """
    if workers < 1:
        raise ValueError("workers must be at least 1")

    by_name = _validate_and_index(packets)
    order = _topological_order(by_name)
    tail = _critical_path(by_name, order)
    finish_by_name: dict[str, float] = {}
    worker_free = [0.0] * workers
    scheduled: list[ScheduledPacket] = []
    remaining = set(by_name)

    while remaining:
        ready = [
            name
            for name in remaining
            if all(parent in finish_by_name for parent in by_name[name].dependencies)
        ]
        if not ready:
            raise RuntimeError("scheduler made no progress on a validated DAG")

        # Prioritize the packet that lies on the longest remaining path.
        name = min(ready, key=lambda n: (-tail[n], n))
        packet = by_name[name]
        worker = min(range(workers), key=lambda i: (worker_free[i], i))
        start = max(
            worker_free[worker],
            max((finish_by_name[parent] for parent in packet.dependencies), default=0.0),
        )
        finish = start + packet.duration
        worker_free[worker] = finish
        finish_by_name[name] = finish
        scheduled.append(ScheduledPacket(name, worker, start, finish))
        remaining.remove(name)

    work = sum(packet.duration for packet in packets)
    critical_path = max(tail.values(), default=0.0)
    makespan = max(finish_by_name.values(), default=0.0)
    return ScheduleResult(
        packets=tuple(scheduled),
        work=work,
        critical_path=critical_path,
        makespan=makespan,
        workers=workers,
    )
