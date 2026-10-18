# Causal Packet Networks (CPN)

**Research proposal:** dependency-structured parallel generation for language models.

A Causal Packet Network represents an answer as a directed acyclic graph (DAG) of variable-length **meaning packets**. Packets that depend on one another are generated in order; independent packets may be generated in parallel. A renderer converts the packet graph into text, and a selective consistency pass checks and repairs only packets that need it.

The research hypothesis is that this can reduce sequential generation rounds and improve whole-answer coherence. It is not yet an implemented model, a measured speedup, or a verified claim of novelty.

## Core question

Can adaptive, dependency-aware packet generation produce better answers with lower end-to-end latency and inference compute than a comparable autoregressive model?

The ambitious target is a 5× improvement in latency and compute alongside better output quality. This is a target to investigate, not a result or promise. Any paper must report measured tradeoffs, including negative results.

## Proposed mechanism

1. **Packetize:** encode a target answer as variable-length semantic units rather than fixed-size token blocks.
2. **Plan dependencies:** connect packets with directed edges for prerequisite information and ordering constraints.
3. **Schedule:** generate packets in parallel when the graph says they are independent; execute dependent packets in later rounds.
4. **Render:** turn packet representations into surface text while preserving the planned structure.
5. **Repair selectively:** detect packet-level contradictions or missing dependencies and recompute only the affected subgraph.

The distinguishing research hypothesis is the combination of **learned variable packet boundaries, an explicit dependency DAG, and critical-path scheduling with local repair**. Each piece has related prior work; novelty must be established through a careful literature review and precise comparison.

## Repository status

This repository currently contains the proposal and pre-registered experiment plan. It does not contain a trained CPN model or empirical results yet.

- [Proposal](PROPOSAL.md)
- [Experiment plan](EXPERIMENT_PLAN.md)

## Principles for reporting

- Separate measured results from hypotheses.
- Count planner, graph, renderer, verifier, retries, and tokenization costs.
- Compare end-to-end latency and actual compute, not only theoretical parallel rounds.
- Use matched baselines and report quality at matched compute as well as compute at matched quality.
- Publish configurations, data versions, seeds, logs, and scripts so results can be reproduced.
- Do not describe the 5× target as achieved unless the experiments show it.

## Suggested first milestone

Build a small controlled prototype and a serial autoregressive baseline on the same compact backbone. Before scaling, test whether packet graphs have useful parallelism, whether graph construction costs erase the benefit, and whether the final text preserves or improves quality. See [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md).

## License

No license has been selected yet. Until one is added, standard copyright applies to the repository contents.
