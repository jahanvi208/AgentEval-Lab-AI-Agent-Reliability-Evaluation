# Frozen experiment protocol

Dataset SHA-256: c24f45f99f7d5f01ef85b2078586da025984f2da021b1e9a645d3bc73b415a64

20 new tasks and four new fixture records: 5 development / 15 test, stratified across five categories. Test values were fixed before any model run. Templates remain related to earlier tasks; no domain-generalization claim. Compare Qwen2.5-0.5B-Instruct and Qwen2.5-1.5B-Instruct across plain, constrained and recovery policies. Same prompt, two generation calls maximum, 256 tokens per call, three host tool calls maximum. Schema repair allowed for all; execution-error replanning only in recovery. Unused budget is not padded. Rotate policy order per task. Greedy CPU inference, two CPU threads. Success requires correct scalar answer plus required tool execution. Do not tune on test results. Syntax constraints do not guarantee semantics or completion before the token cap.
