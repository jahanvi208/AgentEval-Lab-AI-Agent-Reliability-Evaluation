"""Resume an interrupted run, retaining completed task-condition trials."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
from agenteval.models import HFModel
from agenteval.dataset import build,fingerprint
from agenteval.engine import run_task
from agenteval.reporting import summarize,markdown
root=Path(sys.argv[1]);meta=json.loads((root/'metadata.json').read_text());cfg=meta['config']
assert fingerprint(build())==meta['dataset_sha256']
rows=[json.loads(s) for s in (root/'traces.jsonl').read_text().splitlines() if s]
completed={(r['condition'],r['task_id']) for r in rows}
model=HFModel(meta['model'],meta['model_revision'],cfg['max_new_tokens'],cfg['device'])
meta.setdefault('resumptions',[]).append({'utc':datetime.now(timezone.utc).isoformat(),'completed_trials':len(rows)})
(root/'metadata.json').write_text(json.dumps(meta,indent=2))
tasks={t['id']:t for t in build()}
with (root/'traces.jsonl').open('a') as f:
 for condition in cfg['conditions']:
  for task_id in meta['selected_task_ids']:
   if (condition,task_id) in completed:continue
   row=run_task(model,tasks[task_id],condition,cfg['max_steps']);rows.append(row)
   f.write(json.dumps(row)+'\n');f.flush()
   print(condition,task_id,row['success'],flush=True)
summary=summarize(rows)
(root/'summary.json').write_text(json.dumps(summary,indent=2))
(root/'report.md').write_text(markdown(meta,summary))
print('COMPLETED',len(rows),flush=True)
