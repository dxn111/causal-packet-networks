# CPN experiment plan

This plan is written before experiments so that results can be compared fairly. Update it with dated, explicit amendments rather than silently changing success criteria after seeing results.

## Phase 0 — Literature and specification

- Review prior work on multi-token prediction, speculative decoding, diffusion language models, hierarchical latent generation, structured planning, and graph scheduling.
- Build a related-work table stating each method's representation, source of parallelism, verification/repair strategy, reported metric, and difference from CPN.
- Revise the novelty statement before making any “new” or “first” claim.
- Specify packet schema, graph validity rules, renderer interface, and repair trigger.

## Phase 1 — Structural feasibility

Use a public corpus of answers with multi-part structure. Create packet annotations on a small subset, then use the annotations only to test whether meaningful parallel structure exists.

Measure:
- packets per answer and packet length distribution;
- dependency edges and graph density;
- graph critical path divided by node count;
- variation by task type and answer length;
- agreement between annotators or quality of weak labels.

This phase can falsify the premise before training a model. A shallow critical path alone is not evidence of faster inference.

## Phase 2 — Minimal prototype

Use a small open model or compact trained backbone. Implement the simplest complete pipeline:

1. packet planner;
2. dependency graph and ready-node scheduler;
3. batched packet generation;
4. text renderer;
5. graph-level consistency check and local repair.

Keep the same backbone and tokenizer in the serial baseline where feasible. Cache graph and packet representations only when the baseline receives equivalent cache accounting.

First test synthetic graphs and controlled language tasks to validate scheduling and correctness. Label these as systems sanity checks, not language-model quality results.

## Phase 3 — End-to-end comparison

Baselines:
- ordinary autoregressive decoding;
- multi-token or speculative decoding;
- fixed-size block-parallel decoding;
- CPN with full graph generation and repair.

Run batch size 1 and a separate batched setting. Use identical hardware, precision, prompt set, output-length policy, sampling settings, and warm-up protocol.

Measure:
- wall-clock time to first token and full response;
- generated tokens per second;
- end-to-end latency p50 and p95;
- total model forward calls and serial rounds;
- FLOPs, or document the proxy and how it is counted;
- peak memory and energy if measurement hardware supports it;
- planner time, packet generation time, rendering time, checking time, and repair time separately.

Do not infer wall-clock speed from parallel width or round count alone.

## Phase 4 — Quality and ablations

Preselect datasets and metrics before running the main comparison. Include:
- language-model perplexity where comparable;
- task accuracy or exact match on structured tasks;
- coherence, completeness, and contradiction evaluation;
- blinded pairwise human preference for a representative sample.

Ablate:
- fixed versus variable packet size;
- no dependency graph versus learned graph;
- sequential versus ready-node parallel scheduler;
- no repair versus local repair versus full regeneration;
- different packet/edge cost penalties.

Report confidence intervals or repeated-seed variation. Publish all failures and examples of malformed graphs, missing dependencies, inconsistent packets, and repairs that made outputs worse.

## Primary claim rules

- Report **compute savings** separately from **latency speedup**.
- Report **quality gains** separately from **quality preservation**.
- A 5× claim requires at least 5× measured end-to-end improvement on the stated setup, including all CPN overhead.
- A better-output claim requires a predefined metric and uncertainty, or a blinded human study with its protocol disclosed.
- Do not cherry-pick a favorable task or hardware configuration as a general result.
