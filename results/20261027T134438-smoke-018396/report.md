# AgentEval Lab report

SCRIPTED HARNESS SMOKE TEST — NOT MODEL RESULTS

Model: `scripted-smoke-not-an-LLM` | split: dev | dataset SHA-256: `64c8bb037a78031f65eccbabb4486658d294fbea1e404a83627d045d849b219e`

| Condition | Tasks | Success | Accuracy | 95% interval | Mean seconds |
|---|---:|---:|---:|---|---:|
| baseline | 15 | 86.7% | 86.7% | [0.6212, 0.9626] | 0.000 |
| feedback | 15 | 100.0% | 100.0% | [0.7961, 1.0] | 0.000 |
| structured | 15 | 86.7% | 86.7% | [0.6212, 0.9626] | 0.000 |

Success requires the right answer, successful use of required tools and no prohibited-tool attempt.

Conditions share greedy decoding, dataset and step limits. Structured adds a checklist; feedback adds recovery after invalid actions. Feedback may use more inference: compare tokens and latency as well as success.

Wilson intervals are descriptive task-level intervals. Tasks share templates and fixtures, so independence is weak; these are not population-level confidence claims.

Limitations: synthetic data; small template-based task set; no standard external benchmark; direct prompt-injection probes only; no training or fine-tuning; no general safety or research-performance claim.
