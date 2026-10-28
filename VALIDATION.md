# Build validation

- 10 standard-library unit tests passed: deterministic dataset/splits, protocol rejection, finite/type-safe arithmetic, prohibited-tool blocking, required-tool grading, feedback recovery, step limits, scripted execution and confidence interval boundaries.
- Scripted smoke runs completed for both splits (15 development and 45 test tasks), in all three conditions. These are software checks, never model performance evidence.
- Streamlit AppTest rendered the dashboard and exercised condition/category selection, failures-only filtering, and the empty-results state without exceptions. This is programmatic UI testing, not browser visual inspection.
- Python sources compiled; notebook Python cells passed static syntax checks. The Colab notebook and Docker image have not been executed.
- A real Qwen/Qwen2.5-0.5B-Instruct CPU inference check completed on one development task across all three conditions. All three failed the strict final-answer protocol; the raw outputs and observations are preserved in the HF results directory. This validates the inference/reporting path and provides failure evidence, not a performance estimate. At that initial checkpoint, the full test run had not yet been performed; it is now complete as described below.

The environment had Python 3.12, CPU-only PyTorch 2.14.1, Transformers 4.57.6 and Streamlit 1.66.1. Compatibility ranges are in requirements.txt. Model runs record their exact installed versions in metadata.json.

## Completed held-out evaluation

The full 45-task test split completed in all three conditions (135 unique task-condition trials). See FINAL_RESEARCH_REPORT.md and results/20261027T135441-hf-236974. The process was resumed from persisted rows after interruptions; no completed trials were overwritten.

## Grounded execution verification

15 unit tests pass, including forward-reference rejection, prohibited-plan rejection, literal-answer rejection, actual multi-step execution and strict UNKNOWN grading. Real local inference completed 15 development and 45 regression tasks for the planned policy. See GROUNDED_EXECUTION_RESULTS.md.

## Model comparison verification

18 unit tests pass. Real inference completed 90 fresh test trials across two model sizes and three policies; five development tasks were evaluated separately with the small model. See EXPERIMENT_RESULTS.md.
