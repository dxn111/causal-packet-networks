# Causal Packet Networks: A Dependency-Graph Language Model for Parallel Text Generation

**Status:** research proposal; no model or results are claimed.

## Abstract

Autoregressive language models produce text through a sequence of next-token decisions. Parallel decoding methods reduce the number of sequential steps, but fixed token blocks do not directly represent which parts of an answer depend on which other parts. We propose **Causal Packet Networks (CPN)**, a language-modeling approach in which a response is represented as a directed acyclic graph of variable-length semantic packets. Nodes represent pieces of meaning; edges represent information or ordering dependencies. A scheduler generates independent nodes concurrently, while delaying dependent nodes. A surface realizer turns the completed graph into text, and a selective repair mechanism revises only nodes implicated by a consistency failure.

The central hypothesis is that a model can learn a variable-size packet graph that jointly reduces total executed work and the graph’s longest serial chain while preserving or improving answer quality. This differs from asking only whether chunks can be generated concurrently: concurrency may lower latency while increasing total FLOPs. The proposed objective must measure both. This remains a research hypothesis; close prior work overlaps with the broad mechanism, so novelty is unestablished and the exact contribution must be narrowed through direct comparison.

## 1. Motivation

A left-to-right decoder exposes only one next-token step at a time. Many responses contain partially independent content: for example, a list of requirements, several comparison dimensions, or separate supporting reasons. Generating every token in strict sequence may impose unnecessary serial work. On the other hand, generating a fixed block of tokens in parallel can fail when later tokens depend on earlier ones.

CPN asks whether a model can represent those dependencies explicitly and schedule generation around them. Instead of assuming every output position is independent or strictly sequential, it would learn a task-specific graph of semantic work.

## 2. Representation

For an output sequence \(y\), CPN constructs a graph \(G=(V,E)\):

- Each node \(v_i\in V\) is a variable-length packet with a semantic representation and a surface realization.
- A directed edge \((v_i,v_j)\in E\) means packet \(j\) requires information from packet \(i\), or must follow it for discourse or grammatical reasons.
- An antichain is a set of nodes with no dependency path between them. Its packets may be proposed in the same scheduling round.
- A deterministic linearizer or learned renderer maps the graph and packet realizations to a final text sequence.

Packet boundaries and edges are latent or weakly supervised in the initial formulation; they are not assumed to be supplied by a human parser. The model must be trained to find a representation that is both useful for generation and cheap to execute.

## 3. Proposed inference procedure

Given a prompt \(x\):

1. A planner predicts a compact response graph and packet-level representations.
2. The scheduler selects currently ready nodes whose parents are complete.
3. A shared packet generator evaluates ready nodes in a batch, with their parent states as context.
4. A renderer realizes packets into text and orders them according to graph constraints.
5. A consistency checker tests graph-wide constraints. If a conflict or missing prerequisite is detected, only the affected nodes and descendants are regenerated.

The scheduler must account for actual hardware effects. A wider antichain does not imply a wall-clock speedup if batching, graph construction, memory movement, or realization costs dominate.

## 4. Candidate training objective

A first prototype can combine:

- **Text reconstruction:** token-level negative log likelihood of the reference answer after packet realization.
- **Packet semantics:** a representation loss that keeps each packet sufficient to recover its assigned content.
- **Dependency prediction:** predict required edges from training examples or weakly derived dependency labels.
- **Consistency:** penalize contradictions between packet meanings and violations of graph constraints.
- **Execution cost:** penalize measured or estimated serial rounds, expensive packet operations, and repair frequency.

A generic objective is:

\[
\mathcal{L}=\mathcal{L}_{\text{text}}
+\lambda_s\mathcal{L}_{\text{sem}}
+\lambda_e\mathcal{L}_{\text{edge}}
+\lambda_c\mathcal{L}_{\text{consistency}}
+\lambda_b\mathbb{E}[C(G)].
\]

Here \(C(G)\) should eventually include end-to-end measured cost, not only graph depth. The weights and exact parameterization are research choices to be justified experimentally; this equation is a scaffold, not a finalized method.

## 5. Research hypotheses

- **H1 — Useful concurrency:** natural-language answers contain enough independent packet structure to reduce the number of serial generation rounds.
- **H2 — Adaptive boundaries help:** variable-size packets improve the speed-quality frontier over fixed-size token blocks.
- **H3 — Global structure helps quality:** explicit packet dependencies reduce contradictions or omissions on multi-part tasks.
- **H4 — Local repair is cheaper:** selective graph repair costs less than regenerating the entire answer and recovers most quality lost to parallel generation.
- **H5 — End-to-end benefit survives overhead:** planner, scheduler, renderer, and checker costs do not erase the savings.

All hypotheses may fail. In particular, packetization might be noisy, dependencies might be too dense, or a sequential baseline might be faster on real hardware.

## 6. Novelty boundary and related work

The first literature pass found close precedents that substantially overlap with the original broad CPN pitch:

- [PASTA, described in Self-Orchestrating Language Models](https://arxiv.org/abs/2609.14850), trains a model to annotate independently generable output chunks and uses those annotations to parallelize autoregressive decoding. This directly overlaps with semantic chunks plus dependency-aware scheduling.
- [DA-DLM](https://arxiv.org/abs/2609.15070) builds a position-oriented dependency DAG for parallel denoising in diffusion language models.
- [DAPD](https://proceedings.mlr.press/v306/kim26t.html) induces a conditional dependency graph from attention and selects independent tokens for parallel updates in diffusion models.
- [Graph-Structured Speculative Decoding](https://arxiv.org/abs/2407.16207) uses a DAG to organize and share drafted token hypotheses.
- [CoDiLA](https://proceedings.mlr.press/v306/hersche26a.html) combines parallel generation with local autoregressive decoding for coherence.

Therefore, the broad claim “represent an answer as dependent semantic chunks and generate independent chunks in parallel” is not a defensible novelty claim by itself. The name CPN does not make that mechanism new.

A possible narrower contribution to investigate is a **learned variable-size semantic segmentation whose boundaries and dependency graph are optimized jointly for end-to-end measured cost, combined with a constraint-aware local repair procedure**. This is only a candidate distinction. It has not been established as novel, and additional search may find it already covered. The project should first reproduce and compare the closest methods. If the proposed difference is not substantial, frame the work as a reproduction/extension study or choose a different research question.

The paper must include a method-by-method comparison of representation, training target, dependency inference, scheduling, repair, and measured cost. No “first ever” or “never done before” claim should be made without a comprehensive review.

## 7. Evaluation

Compare against matched autoregressive, multi-token/speculative, and fixed-block parallel baselines using the same tokenizer where possible, comparable backbone sizes, training data, decoding settings, and hardware.

Report:

- answer quality on language modeling and task benchmarks;
- human or validated pairwise preference on coherence, completeness, and factual consistency;
- end-to-end latency, time to first token, tokens per second, and latency percentiles;
- measured FLOPs or a clearly defined compute proxy, memory, and energy when available;
- sequential rounds, packet count, graph density, parallel width, repair rate, and repair cost;
- quality at matched compute and compute at matched quality.

Ablations should remove adaptive packet boundaries, dependency edges, parallel scheduling, and selective repair one at a time. Include an oracle graph only as an upper bound, never as a headline practical result.

## 8. Success criteria

The aspirational target is at least 5× higher end-to-end generation throughput and lower inference compute, while improving quality on predefined coherence-sensitive tasks. This target is ambitious and may not be achievable. A valid outcome may be a smaller speed-quality improvement, a benchmark showing the limits of packet parallelism, or a negative result.

A claim of “better output” requires a preselected quality metric or blinded human evaluation with uncertainty estimates. A claim of “5× faster” must be measured end-to-end on identical hardware and decode settings, with planner and repair overhead included.

## 9. Limitations and risks

- Dependency graphs may be difficult to learn without noisy or expensive supervision.
- Natural-language dependencies can be implicit and may make the graph nearly fully sequential.
- Parallel packets may lose local fluency, discourse flow, or factual consistency.
- Graph scheduling and synchronization may be inefficient on small devices.
- Gains may depend on output length, task type, batching, or accelerator.
- A 5× compute reduction, 5× latency improvement, and higher quality are separate claims and must be measured separately.

## 10. Current status

This document defines a research direction. A pure-Python DAG scheduling reference is implemented and unit-tested, but no neural CPN architecture has been implemented, trained, benchmarked, or shown to outperform a baseline.
