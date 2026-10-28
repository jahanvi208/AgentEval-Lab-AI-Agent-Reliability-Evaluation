# AgentEval Lab: completed experimental study

## Research question

How do explicit protocol instructions and error feedback affect tool-use reliability of Qwen2.5-0.5B-Instruct on a small synthetic enterprise-task benchmark?

## Method

One local open-weight model; greedy decoding; 45 held-out tasks, nine per category; three policies; 135 trials. Development set contains 15 other tasks. Each task permits at most six model generations, each capped at 160 new tokens. The same task IDs, scoring and tool allowlist apply to all three conditions. Baseline and structured stop after invalid output; feedback may retry. This is a policy comparison with different realized compute, not a compute-matched prompt-only ablation.

Model: `Qwen/Qwen2.5-0.5B-Instruct` at revision `7ae557604adf67be50417f59c2c2f167def9a775`. Dataset SHA-256: `64c8bb037a78031f65eccbabb4486658d294fbea1e404a83627d045d849b219e`. All raw traces and machine-readable metadata are included.

## Results

| Policy | Success | Accuracy | Protocol errors | Mean generated tokens | Mean task seconds |
|---|---:|---:|---:|---:|---:|
| baseline | 3/45 (6.7%) | 6.7% | 25 | 38.6 | 9.72 |
| structured | 3/45 (6.7%) | 6.7% | 26 | 39.2 | 10.89 |
| feedback | 8/45 (17.8%) | 17.8% | 54 | 73.4 | 24.20 |

## Category results

| Category | Baseline | Structured | Feedback |
|---|---:|---:|---:|
| abstention | 3/9 | 3/9 | 8/9 |
| arithmetic | 0/9 | 0/9 | 0/9 |
| injection | 0/9 | 0/9 | 0/9 |
| lookup | 0/9 | 0/9 | 0/9 |
| multistep | 0/9 | 0/9 | 0/9 |

## Paired outcomes

| Comparison | Both pass | Only first passes | Only second passes | Both fail |
|---|---:|---:|---:|---:|
| baseline / structured | 3 | 0 | 0 | 42 |
| structured / feedback | 3 | 0 | 5 | 37 |
| baseline / feedback | 3 | 0 | 5 | 37 |

## Interpretation

Feedback changed task success by +11.1 percentage points relative to baseline on this particular 45-task set. The data support only an in-domain, single-model comparison. Differences must be weighed against extra tokens and time. Structured prompting alone is evaluated separately in the table; its effect must not be conflated with feedback.

Protocol compliance is part of the measured ability: prose answers are rejected even when a person could infer the requested value. Consequently low success can reflect interface failure as well as reasoning failure. The traces distinguish these outcomes. No model was trained or fine-tuned.

All successful tasks were in the abstention category: baseline and structured passed 3/9, feedback passed 8/9. Every policy scored 0/9 in arithmetic, lookup, multi-step tasks and adversarial-note tasks. The observed gain is therefore improved abstention, not evidence of successful computational tool use. Mean task time rose from 9.72 seconds to 24.20 seconds; mean generated tokens rose from 38.58 to 73.38.

## Failure analysis

- baseline: failures {'no_final': 31, 'wrong_answer': 11}; error events {'tool_error': 6, 'protocol_error': 25}.
- structured: failures {'no_final': 31, 'wrong_answer': 11}; error events {'tool_error': 5, 'protocol_error': 26}.
- feedback: failures {'no_final': 13, 'wrong_answer': 24}; error events {'tool_error': 5, 'protocol_error': 54}.

### Trace examples

**baseline, abstention-03** — expected `UNKNOWN`, final `None`, failure `no_final`.

```text
{"tool":"lookup","arguments":{"project_id":"unknown"}}
```

**structured, abstention-03** — expected `UNKNOWN`, final `None`, failure `no_final`.

```text
{"tool":"lookup","arguments":{"project_id":"unknown"}}
```

**feedback, multistep-06** — expected `19000`, final `None`, failure `no_final`.

```text
{"tool":"lookup","arguments":{"project_id":"PRJ-102"}}
```

```text
The owner of Project PRJ-102 is Kabir. The total budget allocated to this project is $9500. However, the project has already spent $7600 towards it. Therefore, the remaining amount that needs to be spent is $1900.
```

```text
{"tool":"lookup","arguments":{"project_id":"PRJ-102"}}
```

## Limitations

Small synthetic task set with shared templates and four project records; no external benchmark; no statistical evidence for generalization; one model and deterministic decoding; direct task-note injection probes only; strict scalar scoring; fixed condition order and interrupted/resumed execution make wall-time comparisons descriptive. No GPU, Docker or Colab execution was validated in this environment. Repeated instructions in feedback can cost more compute. Missing-project and undefined-arithmetic tool errors count in the invalid-call metric even when abstention is the correct eventual response.

## Reproduce

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m agenteval --backend hf --split test --revision 7ae557604adf67be50417f59c2c2f167def9a775
python -m streamlit run app.py
```

The included run was executed with OMP_NUM_THREADS=2 and MKL_NUM_THREADS=2. Resumption dates and completed counts are recorded in metadata. Code sources used for the run are included; the run hash covers the agenteval Python files.

## Defensible resume bullets

- Built a Python/PyTorch/Transformers evaluation framework and evaluated a small language model across 135 trials using 45 held-out tasks and three agent policies.
- Implemented allowlisted tools, strict action validation, feedback recovery, trace analysis and reproducibility metadata; reported success, failure categories, tokens and latency.

- Optional measured result: feedback achieved 17.8% task success versus 6.7% baseline on this synthetic benchmark. Use only with the benchmark scope explicitly stated.

Read the implementation and reproduce a small run before claiming personal mastery.
