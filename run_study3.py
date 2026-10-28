"""Run the frozen test matrix sequentially; invocation is resumable per trial."""
import os,subprocess,sys
from pathlib import Path
root=Path(__file__).parent
env=dict(os.environ,OMP_NUM_THREADS='2',MKL_NUM_THREADS='2')
for label,model in [('small','Qwen/Qwen2.5-0.5B-Instruct'),('large','Qwen/Qwen2.5-1.5B-Instruct')]:
 with (root/f'v3-{label}-test.log').open('a') as log:
  result=subprocess.run([sys.executable,'-m','agenteval.study3','--model',model,'--split','test','--output',f'results/v3-{label}-test'],cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise SystemExit(result.returncode)
 print('COMPLETED MODEL',label,flush=True)
