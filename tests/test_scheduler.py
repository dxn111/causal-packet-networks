import unittest

from research.scheduler import Packet, schedule_packets


class SchedulerTests(unittest.TestCase):
    def test_chain_cannot_be_parallelized(self):
        packets = [
            Packet("a", 2),
            Packet("b", 3, ("a",)),
            Packet("c", 1, ("b",)),
        ]
        result = schedule_packets(packets, workers=4)
        self.assertEqual(result.work, 6)
        self.assertEqual(result.critical_path, 6)
        self.assertEqual(result.makespan, 6)

    def test_independent_packets_run_in_parallel(self):
        packets = [Packet("a", 3), Packet("b", 2), Packet("c", 1)]
        result = schedule_packets(packets, workers=2)
        self.assertEqual(result.work, 6)
        self.assertEqual(result.critical_path, 3)
        self.assertEqual(result.makespan, 3)

    def test_diamond_respects_join_dependency(self):
        packets = [
            Packet("root", 2),
            Packet("left", 3, ("root",)),
            Packet("right", 4, ("root",)),
            Packet("join", 2, ("left", "right")),
        ]
        result = schedule_packets(packets, workers=2)
        self.assertEqual(result.work, 11)
        self.assertEqual(result.critical_path, 8)
        self.assertEqual(result.makespan, 8)
        start = {packet.name: packet.start for packet in result.packets}
        finish = {packet.name: packet.finish for packet in result.packets}
        self.assertGreaterEqual(start["join"], finish["left"])
        self.assertGreaterEqual(start["join"], finish["right"])

    def test_cycle_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            schedule_packets(
                [Packet("a", 1, ("b",)), Packet("b", 1, ("a",))], workers=2
            )

    def test_unknown_dependency_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown dependencies"):
            schedule_packets([Packet("a", 1, ("missing",))], workers=1)

    def test_invalid_duration_and_worker_count_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "negative duration"):
            schedule_packets([Packet("a", -1)], workers=1)
        with self.assertRaisesRegex(ValueError, "workers"):
            schedule_packets([Packet("a", 1)], workers=0)


if __name__ == "__main__":
    unittest.main()
