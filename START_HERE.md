Read the [experiment results](EXPERIMENT_RESULTS.md) first, then open the dashboard to explore the completed runs.

**Finished results:** open FINAL_RESEARCH_REPORT.md first. The dashboard can display the included complete experiment without rerunning inference.

# Start here

Extract the ZIP and open `agentEval-lab` in VS Code. Run these commands in its terminal:

```bash
python -m unittest discover -s tests -v
python -m agenteval --backend smoke
```

This verifies the harness without any downloads. For actual model evaluation:

```bash
python -m pip install -r requirements.txt
python -m agenteval --backend hf --split dev --limit 3
streamlit run app.py
```

First run downloads model weights. CPU inference may be slow on your laptop. For a GPU alternative, open `AgentEval_Colab.ipynb` in Colab, select a GPU runtime, and upload the original project ZIP when prompted. No API key is needed.

Read `README.md` for the method, `VALIDATION.md` for completed checks, and `RESEARCH_NOTES.md` before writing resume claims. Inspect traces and understand one task end to end before citing this project.
