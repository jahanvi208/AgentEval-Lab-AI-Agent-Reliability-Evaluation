# AgentEval Lab: grounded execution

## What changed

Added a fourth agent policy, `planned`. The language model proposes a bounded plan. Python validates the complete plan before executing allowlisted tools. Arguments can reference earlier tool results, and the final answer must reference an actual tool output. The host resolves the final value without asking the model to rewrite it. Literal guessed answers are rejected, except explicit UNKNOWN abstention. Missing records and division by zero permit host abstention. Invalid plans get one schema-repair attempt. Unknown tools reject the plan before execution.

This moves answer transport and reference resolution into deterministic code while leaving semantic tool selection and argument planning with the model. A model can still choose the wrong operation, project, field or abstention; these remain failures.

## Measured regression results

| Policy | Success / 45 | Mean tokens | Mean seconds |
|---|---:|---:|---:|
| baseline | 3/45 | 38.6 | 9.72 |
| feedback | 8/45 | 73.4 | 24.20 |
| structured | 3/45 | 39.2 | 10.89 |
| planned | 10/45 | 42.6 | 14.01 |

| Category | Planned successes / 9 |
|---|---:|
| abstention | 3/9 |
| arithmetic | 2/9 |
| injection | 0/9 |
| lookup | 5/9 |
| multistep | 0/9 |

## Interpretation and limits

The planned policy achieved 22.2% on the original 45-task regression suite. Do not describe a dev or regression result as evidence of unseen-task generalization. The original test results were already inspected before this redesign. The 15-task development pass achieved 3/15, and was retained as a separate run. No prompt changes were made after that pass.

The new policy has two planning generations capped at 256 tokens each and at most three host tool calls; the original policies allow up to six generations capped at 160 tokens each. The new prompt has additional demonstrations. This is a complete architecture comparison with different budgets and prompting, not an isolated causal test of grounding. Model size, dataset and strict correctness checks remain unchanged. Timing spans interrupted runs and is descriptive.

The software architecture is stronger: tool-output references and complete plan validation make some failures impossible by construction. The empirical tables determine whether this particular model used it effectively. No inflated reliability or general safety claim is warranted.

## Run

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m agenteval --backend hf --split dev --conditions planned --max-new-tokens 256
python -m agenteval --backend hf --split test --conditions planned --max-new-tokens 256
python -m streamlit run app.py
```

## Evidence

Original study: FINAL_RESEARCH_REPORT.md. Original code: archive/v1/agenteval. New run: results/20261027T144453-hf-033463. All model outputs, tool observations, validation failures and run metadata are included. The existing default still runs the original three conditions; select planned explicitly.

## Resume scope

Describe this as an agent evaluation and reliability engineering project. Mention validated plan execution, bounded recovery, trace inspection and measured comparisons. Do not claim fine-tuning, a publication, production-grade reliability or unseen-domain performance.
