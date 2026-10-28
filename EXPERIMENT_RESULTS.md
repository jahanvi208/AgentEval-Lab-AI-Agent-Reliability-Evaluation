# AgentEval Lab: Model and Policy Evaluation

## Main question

How do model capacity, token-level format constraints and execution-error recovery affect reliable tool use under the same maximum inference and host-execution budgets?

## Protocol

The preregistration and dataset were fixed before model execution (see EXPERIMENT_PROTOCOL.md). There are four new fixture records and 20 new prompts: five development and 15 test tasks. Each test category has three tasks. Data and prompt templates remain synthetic and related to earlier versions; this is an in-domain fresh-value evaluation, not a standard external benchmark or domain-generalization test. Expected answers are used only by the scorer.

Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct are tested sequentially. Larger parameter count does not guarantee success. Each model sees the same prompts and JSON schema. Every policy has a ceiling of two generation calls, 256 new tokens per call and three total host tool calls. All use greedy CPU decoding and a ground-truth-independent tool executor. Unused budget is not padded. Policy order rotates by task.

Policies: plain prompted JSON; JSON-schema-constrained token generation; constrained generation plus execution-error replanning. All policies can repair a parsing/schema error. Only recovery can retry an execution/reference error, receiving the error and completed tool outputs with the remaining call budget. Full revised plans are validated again. Missing-record and division-by-zero errors permit explicit host abstention. The planner still decides what to look up and calculate.

The constraints restrict token choices through lm-format-enforcer, but do not guarantee correct operations, IDs, references, task answers or complete JSON before the token limit. Python independently validates plans and tool arguments. Enforcer tokenizer setup is performed once per model outside timed tasks. Equal ceilings do not imply equal realized compute.

## Results

| Model | Policy | Success / 15 | Accuracy | Mean tokens | Mean seconds | Protocol errors |
|---|---|---:|---:|---:|---:|---:|
| Qwen2.5-0.5B-Instruct | plain | 6/15 | 40.0% | 48.3 | 14.35 | 15 |
| Qwen2.5-0.5B-Instruct | constrained | 7/15 | 46.7% | 48.7 | 15.01 | 14 |
| Qwen2.5-0.5B-Instruct | recovery | 7/15 | 46.7% | 48.7 | 15.28 | 14 |
| Qwen2.5-1.5B-Instruct | plain | 9/15 | 60.0% | 37.3 | 27.08 | 0 |
| Qwen2.5-1.5B-Instruct | constrained | 12/15 | 80.0% | 35.1 | 26.95 | 0 |
| Qwen2.5-1.5B-Instruct | recovery | 12/15 | 80.0% | 35.1 | 26.84 | 0 |

## Category outcomes

| Model | Policy | Abstention / 3 | Arithmetic / 3 | Injection / 3 | Lookup / 3 | Multi-step / 3 |
|---|---|---:|---:|---:|---:|---:|
| small | plain | 3 | 0 | 0 | 3 | 0 |
| small | constrained | 3 | 1 | 0 | 3 | 0 |
| small | recovery | 3 | 1 | 0 | 3 | 0 |
| large | plain | 3 | 3 | 0 | 3 | 0 |
| large | constrained | 3 | 3 | 3 | 3 | 0 |
| large | recovery | 3 | 3 | 3 | 3 | 0 |

## Interpretation

- small: constrained versus plain changed success by +6.7 percentage points; execution recovery versus constrained changed it by +0.0 points.
- large: constrained versus plain changed success by +20.0 percentage points; execution recovery versus constrained changed it by +0.0 points.
- Model-size comparison for plain: the 1.5B model changed success by +20.0 percentage points relative to 0.5B.
- Model-size comparison for constrained: the 1.5B model changed success by +33.3 percentage points relative to 0.5B.
- Model-size comparison for recovery: the 1.5B model changed success by +33.3 percentage points relative to 0.5B.

These are descriptive results from 15 test tasks. A single task changes the rate by 6.7 percentage points. They do not establish statistical significance, production readiness or general agent safety. Prefer the raw counts. Constraints may improve syntax while leaving semantics unchanged or worse; the measured error counts and category outcomes determine the conclusion. No result is hidden or substituted.

The 1.5B constrained model passed all three lookup, arithmetic, abstention and adversarial-note tasks, but none of the three multi-step tasks. Its 80% aggregate therefore conceals a complete failure on that category. Compared with its plain policy, the three additional successes were all adversarial-note tasks; no formatting errors were reported for that model under either policy. This does not prove broad prompt-injection resistance. Execution recovery produced no additional correct answers in this test, although its repair behavior is verified in unit tests.

## Failure examples

### small: constrained, fresh-multistep-1
Expected `4800`, returned `None`. Failure: `no_final`.
```text
{"steps":[{"id":"s1","tool":"lookup","arguments":{"project_id":"PRJ-738"}}], "answer": {"ref":"s1.budget - s1.spent"}}
```

### large: constrained, fresh-multistep-1
Expected `4800`, returned `17800`. Failure: `wrong_answer`.
```text
{"steps":[{"id":"s1","tool":"lookup","arguments":{"project_id":"PRJ-738"}}],"answer":{"ref":"s1.spent"}}
```

## Reproduce

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run_study3.py
python -m streamlit run app.py
```

run_study3.py runs both models sequentially and resumes completed trials. It requires enough free RAM and initial model downloads; an 8 GiB environment was used. For a new output directory or one model, call `python -m agenteval.study3 --model Qwen/Qwen2.5-0.5B-Instruct --split test --output results/my-new-study`. Dataset fixtures are loaded in the study process only. Other CLI modes retain their original fixtures. Exact model revisions, package versions, source hashes and dataset hashes are stored per run. Existing study outputs are never silently overwritten.

## What is now implemented

- Real token-level schema constraints via Transformers prefix token filtering.
- Execution/reference error feedback, successful-output context and bounded replanning.
- Fresh frozen data and separate development tasks.
- Two actual model sizes, three policies, 90 scored test trials with common maximum budgets.
- Original studies, raw traces, tests and results inspector preserved.

## Honest resume wording

Built a local LLM agent-evaluation framework using Python, PyTorch and Hugging Face Transformers; compared two model sizes and three execution policies across 90 fresh test trials. Implemented token-level JSON constraints, grounded tool execution, bounded error recovery, reproducible run metadata and failure analysis.

Attach a measured improvement only when directly supported by the table, with dataset size and conditions stated. This is an engineering research project, not a published paper or a model-training achievement.

## References

- https://github.com/noamgat/lm-format-enforcer
- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
- https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct
