**Completed results are in FINAL_RESEARCH_REPORT.md.** The worksheet below records the original pre-experiment plan; its unfilled table is not the current result.

# Experiment worksheet

## Before running

Research question: Does schema-focused instruction and error feedback improve tool-use reliability for this small instruction model?

Fix model ID/revision, dataset fingerprint, step limit, generated-token limit, decoding, hardware and software versions. Use development tasks to debug; do not tune on the held-out split. Prompt text is in engine.py.

## Results to fill after actual model execution

| Condition | Success / total | Protocol errors | Invalid tool calls | Tokens | Latency |
|---|---|---|---|---|---|
| baseline | Not measured | Not measured | Not measured | Not measured | Not measured |
| structured | Not measured | Not measured | Not measured | Not measured | Not measured |
| feedback | Not measured | Not measured | Not measured | Not measured | Not measured |

For the paired comparison, list task IDs where one condition succeeds and the other fails. Inspect whether recovery was due to syntax repair, argument repair, or correct abstention. Report negative results. Do not cherry-pick successful tasks or merge development and test scores.

## Further work

Add unseen project fixtures and paraphrases, native function-calling model adapters, a public external tool-use benchmark, human review of attack outcomes, model-size comparisons, balanced timing order and a compute-matched retry control. Fine-tuning with PEFT is a separate future experiment and must not be claimed here.

## Resume wording

After understanding the code and running it yourself:

**AgentEval Lab — Python, Hugging Face Transformers, PyTorch**
- Developed a reproducible evaluation harness comparing three tool-use policies on 60 synthetic tasks spanning arithmetic, lookup, multi-step workflows, abstention and adversarial instructions.
- Implemented allowlisted tools, schema validation, execution traces, failure analysis and run metadata with dataset and model revisions.

Only add model-specific results and Streamlit/Docker experience once you have run and can explain those components. Included smoke tests and the one-task model check do not substantiate general model performance claims.
