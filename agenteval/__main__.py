import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
import time
from datetime import datetime,timezone
from pathlib import Path
from .dataset import build,fingerprint
from .engine import CONDITIONS,run_task
from .models import HFModel,ScriptedModel
from .reporting import summarize,markdown


def main():
    p=argparse.ArgumentParser(description='Run a local tool-use experiment; smoke mode is NOT an LLM benchmark.')
    p.add_argument('--backend',choices=['smoke','hf'],default='smoke')
    p.add_argument('--model',default='Qwen/Qwen2.5-0.5B-Instruct')
    p.add_argument('--revision',help='Hugging Face commit SHA for exact reruns')
    p.add_argument('--device',choices=['cpu','cuda'],default='cpu')
    p.add_argument('--split',choices=['dev','test'],default='dev')
    p.add_argument('--conditions',nargs='+',choices=CONDITIONS,default=["baseline","structured","feedback"])
    p.add_argument('--limit',type=int,help='Task subset for quick checks, not full benchmark')
    p.add_argument('--max-steps',type=int,default=6)
    p.add_argument('--max-new-tokens',type=int,default=160)
    p.add_argument('--output',default='results')
    args=p.parse_args()
    if args.max_steps<1 or args.max_new_tokens<1 or (args.limit is not None and args.limit<1):p.error('limits must be positive')
    tasks=build();selected=[t for t in tasks if t['split']==args.split]
    if args.limit:selected=selected[:args.limit]
    model=ScriptedModel() if args.backend=='smoke' else HFModel(args.model,args.revision,args.max_new_tokens,args.device)
    out=Path(args.output)/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+args.backend+'-'+str(time.time_ns())[-6:])
    out.mkdir(parents=True,exist_ok=False)
    versions={}
    for pkg in ('torch','transformers','tokenizers','streamlit'):
        try:versions[pkg]=importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:pass
    metadata={'backend':model.kind,'model':model.model_id,'model_revision':model.revision,'split':args.split,'dataset_sha256':fingerprint(tasks),'selected_task_ids':[t['id'] for t in selected], 'config':vars(args),'python':sys.version,'platform':platform.platform(),'packages':versions,'seed':42,'decoding':'greedy','created_utc':datetime.now(timezone.utc).isoformat(),'code_sha256':hashlib.sha256(b''.join(f.read_bytes() for f in sorted(Path(__file__).parent.glob('*.py')))).hexdigest()}
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    rows=[]
    with (out/'traces.jsonl').open('w',encoding='utf-8') as f:
        for condition in dict.fromkeys(args.conditions):
            for task in selected:
                row=run_task(model,task,condition,args.max_steps)
                rows.append(row);f.write(json.dumps(row)+'\n');f.flush()
                print(f"{condition:10} {task['id']:18} {'PASS' if row['success'] else row['failure']}",flush=True)
    summary=summarize(rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (out/'report.md').write_text(markdown(metadata,summary),encoding='utf-8')
    print(f'Report: {out / "report.md"}')

if __name__=='__main__':main()
