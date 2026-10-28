# AgentEval Lab — AI Agent Reliability Evaluation

## Latest completed experiment (v3)

Evaluates agent failures through controlled experiments with two local language models and three execution policies: plain plans, schema-constrained plans, and constrained plans with error recovery. Includes executable Python code, a Streamlit dashboard, raw model traces, tests, and experiment reports.

**90 test trials** across 15 fresh synthetic tasks, two models, and three policies:

| Model | Plain | Schema-constrained | With recovery |
|---|---:|---:|---:|
| Qwen2.5-0.5B-Instruct | 6/15 | 7/15 | 7/15 |
| Qwen2.5-1.5B-Instruct | 9/15 | 12/15 | 12/15 |

All policies share caps of two generations, 256 tokens per generation, and three host tool calls. Schema constraints improved observed success; recovery added no successes in this sample. All three multi-step test tasks still failed for the larger model. These are small synthetic, in-domain experiments, not evidence of production reliability or statistical significance.

Read [v3 results](V3_RESULTS.md), [frozen protocol](V3_PREREGISTRATION.md), and [validation](VALIDATION.md). Historical studies below use different datasets and should not be compared directly with v3 scores.

### Open the dashboard without downloading models

```bash
git clone https://github.com/jahanvi208/AgentEval-Lab-AI-Agent-Reliability-Evaluation.git
cd AgentEval-Lab-AI-Agent-Reliability-Evaluation
python -m pip install "streamlit>=1.50,<2"
python -m streamlit run app.py
```

The dashboard displays the included completed results. To test the software, run `python -m unittest discover -s tests -v` (18 tests; no model download required). To reproduce or resume v3, install `requirements.txt` and run `python run_study3.py`; completed trials are skipped. See [the v3 notebook](AgentEval_v3_Colab.ipynb) for its workflow and the CPU requirements below.

## Original study and implementation

A Python experiment harness for small language model tool-use reliability. It compares **baseline**, **structured instructions**, and **structured instructions with error feedback** on the same synthetic tasks. Includes local Hugging Face inference, strict tool dispatch, trace-level scoring, reproducibility metadata and a Streamlit results inspector.

**Completed study:** 135 actual model trials across 45 held-out tasks and three policies. See `FINAL_RESEARCH_REPORT.md` for measured results, failure analysis and limitations. Raw traces are included. Smoke data remain explicitly labelled.

## Quick start — Windows / VS Code

Requires Python 3.10+ (3.11 recommended). Extract this directory, open a terminal inside it.

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m unittest discover -s tests -v
python -m agenteval --backend smoke --split dev
```

Those commands use only Python's standard library and verify the evaluation software. Linux/macOS activation: `source .venv/bin/activate`.

For real local model experiments and the dashboard:

```powershell
python -m pip install -r requirements.txt
python -m agenteval --backend hf --split dev --limit 3
streamlit run app.py
```

The default model is `Qwen/Qwen2.5-0.5B-Instruct`. First run downloads its weights. This uses local CPU inference; no paid API or key. A Ryzen 3 laptop may be slow and needs enough free RAM. Start with three tasks. For faster runs use a GPU machine or a notebook GPU and `--device cuda`. GPU runs still load FP32 weights in this implementation. No claim that this model has native reliable function calling: we evaluate a prompted JSON protocol.

## Research question and hypotheses

Does an explicit action-format checklist improve successful tool use? Does error feedback recover failures under a fixed six-generation budget? Both are **hypotheses, not established findings**.

| Condition | Tool schemas | Extra checklist | Recover invalid actions |
|---|---|---|---|
| baseline | Yes | No | No |
| structured | Yes | Yes | No |
| feedback | Yes | Yes | Yes |

This compares agent policies, not just prompt wording: baseline and structured stop on an invalid action. Feedback receives a concrete error and may retry, within the same total step budget. All conditions use the same underlying model and greedy decoding. Valid tool results are provided in all conditions. Recovery has extra compute costs; inspect generated tokens and latency. There is no unsupported no-tool model baseline or retrieval intervention.

## Benchmark

60 synthetic English tasks, 12 per category: arithmetic, project lookup, multi-step arithmetic over records, abstention, and adversarial instructions embedded in untrusted task notes. Four synthetic project records; no real enterprise data. Tool allowlist: `lookup` and `calculate`. No shell, network, file writes, email or arbitrary expression evaluation is exposed to the model.

15 development / 45 test tasks, deterministically stratified by category. Test prompts are distinct, but templates and fixture records are shared. This is a small in-domain benchmark, not evidence of generalization to unseen domains. The model receives only task prompts, public tool schemas and previous observations: never expected answers or grading rules from task records.

Inspect the versioned `data/tasks.jsonl`. The runner regenerates the canonical dataset through `dataset.build()`; changes to the JSONL alone do not alter runs. To change tasks, edit the builder, regenerate JSONL and rerun tests. Each run fingerprints the complete canonical dataset.

## Run a controlled study

1. Use dev tasks to debug prompts; keep test results unseen during prompt development.
2. Choose model and model revision before the final test run.
3. Run all three conditions on test tasks with identical configuration.
4. Inspect task traces and compare category outcomes, tokens, latency, and errors.
5. Record failures and limitations, including any negative or null result.

```powershell
python -m agenteval --backend hf --model Qwen/Qwen2.5-0.5B-Instruct --split dev
python -m agenteval --backend hf --model Qwen/Qwen2.5-0.5B-Instruct --split test
```

Metadata stores the resolved model commit. To reproduce it, pass the returned SHA with `--revision`. Record dependencies using `python -m pip freeze > environment-lock.txt` after successful installation. Supplied requirements are compatibility ranges, not an exact lockfile. Model licensing remains governed by each model publisher.

Every run creates a unique directory containing `metadata.json`, `traces.jsonl`, `summary.json`, and `report.md`. Completed runs appear in the dashboard. If loading/inference fails, the command exits with an error: it never falls back to fabricated responses. A failed run may retain partial traces; it has no completed summary.

## Metrics

- **Answer accuracy:** exact normalized text or numeric tolerance (1e-4). JSON scalar answers only.
- **Task success:** correct answer, successful execution of every required tool type, and no prohibited-tool attempt. Not a proof of causal grounding.
- **Invalid tool call rate:** unknown-tool plus tool-execution errors / all attempted tool calls. Includes expected environmental errors such as missing records; interpret alongside traces. Protocol errors are reported separately.
- **Policy compliance:** no attempt to call an unknown tool. Does not certify general agent safety.
- **Latency:** full task wall time; model load excluded; first generation may include warm-up. P95 uses the nearest rank. Condition order is fixed, so timing is descriptive, not a rigorous performance benchmark.
- **Intervals:** Wilson 95% task-level intervals. Shared templates violate strong independence assumptions; do not overinterpret significance.

## Files

- `agenteval/engine.py`: action protocol, agent loop and grading
- `agenteval/tools.py`: allowlist and deterministic sandbox
- `agenteval/models.py`: real local Transformers and labelled scripted smoke backends
- `agenteval/dataset.py`: deterministic task generation and split
- `agenteval/reporting.py`: aggregate metrics and Markdown report
- `app.py`: read-only run inspector
- `tests/test_core.py`: grading, safety boundaries, recovery and dataset tests
- `RESEARCH_NOTES.md`: experiment worksheet and honest resume wording

## Docker (optional)

```bash
docker build -t agenteval-lab .
docker run --rm -p 8501:8501 agenteval-lab
```

This launches the results viewer. To generate a run inside a container: `docker run --rm -v "${PWD}/results:/app/results" agenteval-lab python -m agenteval --backend smoke`. Real HF runs additionally need weight downloads and sufficient RAM. Docker configuration is provided but was not executed in the build environment.

## References

- Qwen model card: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
- Transformers chat templates: https://huggingface.co/docs/transformers/chat_templating
- Transformers tool support: https://huggingface.co/docs/transformers/chat_template_tools_and_documents

We use the model's ordinary chat template and an explicit JSON protocol. This is an original small engineering benchmark, not a reproduction of a published paper. No LoRA, RLHF, distillation, retrieval system or accelerator optimization is implemented.


## CPU setup for the v3 study

Both models use CPU float32 inference in the frozen v3 runner. The 1.5B model alone needs roughly 6 GB for weights, plus runtime overhead; leave sufficient free RAM. For a CPU-only PyTorch installation, install `torch` from https://download.pytorch.org/whl/cpu before installing requirements.txt. Initial runs download model weights; no API key is needed. Use AgentEval_v3_Colab.ipynb for a notebook workflow. GPU execution is available in the older CLI, but was not added to or tested in the frozen v3 runner.
