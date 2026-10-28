"""Fresh, preregistered model-by-policy study with identical generation ceilings."""
import argparse,hashlib,json,time,platform,sys,importlib.metadata
from pathlib import Path
from datetime import datetime,timezone
from .models import HFModel
from .planned import PROMPT,parse_plan,resolve,PlanError
from .engine import equal_answer
from .tools import execute,ToolError,RECORDS
from .reporting import summarize

REF={'type':'object','properties':{'ref':{'type':'string'}},'required':['ref'],'additionalProperties':False}
VALUE={'anyOf':[{'type':'number'},REF]}
SCHEMA={'type':'object','properties':{'steps':{'type':'array','maxItems':3,'items':{'type':'object','properties':{'id':{'type':'string','enum':['s1','s2','s3']},'tool':{'type':'string','enum':['lookup','calculate']},'arguments':{'type':'object','properties':{'project_id':{'type':'string'},'operation':{'type':'string','enum':['add','subtract','multiply','divide']},'a':VALUE,'b':VALUE},'additionalProperties':False}},'required':['id','tool','arguments'],'additionalProperties':False}},'answer':{'anyOf':[REF,{'type':'string','enum':['UNKNOWN']}]}},'required':['steps','answer'],'additionalProperties':False}

class SchemaModel(HFModel):
 def generate_plan(self,messages,constrained):
  import torch
  from lmformatenforcer import JsonSchemaParser
  from lmformatenforcer.integrations.transformers import build_transformers_prefix_allowed_tokens_fn
  text=self.tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
  inputs=self.tokenizer(text,return_tensors='pt',add_special_tokens=False).to(self.device)
  options={}
  if constrained:options['prefix_allowed_tokens_fn']=build_transformers_prefix_allowed_tokens_fn(self.tokenizer,JsonSchemaParser(SCHEMA))
  with torch.inference_mode():out=self.model.generate(**inputs,max_new_tokens=256,do_sample=False,pad_token_id=self.tokenizer.eos_token_id,**options)
  generated=out[0,inputs['input_ids'].shape[1]:]
  return self.tokenizer.decode(generated,skip_special_tokens=True),len(generated)

def trial(model,task,policy):
 messages=[{'role':'system','content':PROMPT},{'role':'user','content':task['prompt']}]
 trace=[];errors=[];calls=[];final=None;tokens=0;start=time.perf_counter();executed=0
 for attempt in range(2):
  raw,n=model.generate_plan(messages,policy!='plain');tokens+=n
  trace.append({'step':len(trace)+1,'raw':raw,'attempt':attempt+1})
  try:plan=parse_plan(raw)
  except (ValueError,TypeError) as exc:
   kind='unknown_tool' if 'prohibited tool' in str(exc) else 'protocol_error'
   errors.append(kind);trace[-1].update(error_type=kind,error=str(exc))
   if kind=='unknown_tool':break
   feedback='Schema error: '+str(exc)
  else:
   outputs={};feedback=None
   try:
    if not plan['steps']:final='UNKNOWN';break
    if executed+len(plan['steps'])>3:raise PlanError('Remaining host tool budget exceeded')
    for step in plan['steps']:
     args={k:resolve(v,outputs) for k,v in step['arguments'].items()};executed+=1;calls.append(step['tool'])
     e={'step':len(trace)+1,'raw':'[host executes plan]','tool':step['tool'],'arguments':args};trace.append(e)
     value=execute(step['tool'],args);outputs[step['id']]=value;e['observation']=value
    final=resolve(plan['answer'],outputs);break
   except ToolError as exc:
    errors.append('tool_error');trace[-1].update(error_type='tool_error',error=str(exc))
    if str(exc).startswith(('project not found','division by zero')):final='UNKNOWN';break
    feedback='Execution error: '+str(exc)+'; successful outputs: '+json.dumps(outputs)
    if policy!='recovery':break
   except (ValueError,KeyError,TypeError) as exc:
    errors.append('protocol_error');trace[-1].update(error_type='protocol_error',error=str(exc))
    feedback='Reference/execution error: '+str(exc)+'; successful outputs: '+json.dumps(outputs)
    if policy!='recovery':break
  messages.extend([{'role':'assistant','content':raw},{'role':'user','content':feedback+'. Revise only the failed plan. At most '+str(3-executed)+' tool calls remain. Return a complete JSON plan; use known outputs as numeric arguments when helpful.'}])
 correct=equal_answer(final,task['expected']);complete=all(any(e.get('tool')==t and 'observation' in e for e in trace) for t in task['required_tools'])
 safe='unknown_tool' not in errors;success=correct and complete and safe
 return dict(task_id=task['id'],category=task['category'],condition=policy,expected=task['expected'],final=final,correct=correct,required_tools_complete=complete,policy_compliant=safe,success=success,failure=None if success else 'no_final' if final is None else 'wrong_answer' if not correct else 'missing_required_tool',errors=errors,calls=calls,steps=len(trace),seconds=time.perf_counter()-start,tokens=tokens,trace=trace)

def main():
 p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--split',choices=['dev','test'],default='test');p.add_argument('--output',required=True);a=p.parse_args()
 dataset=Path(__file__).parents[1]/'data/fresh_v3.json';raw=dataset.read_bytes();data=json.loads(raw)
 RECORDS.clear();RECORDS.update(data['records'])
 out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
 meta_path=out/'metadata.json';previous=json.loads(meta_path.read_text()) if meta_path.exists() else None
 model=SchemaModel(a.model,revision=previous['model_revision'] if previous else None,max_new_tokens=256)
 tasks=[t for t in data['tasks'] if t['split']==a.split]
 metadata={'backend':'huggingface_local','model':a.model,'model_revision':model.revision,'split':a.split,'dataset_sha256':hashlib.sha256(raw).hexdigest(),'budget':{'generation_calls':2,'tokens_per_call':256,'host_tool_calls':3},'policies':['plain','constrained','recovery'],'selected_task_ids':[t['id'] for t in tasks],'created_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'packages':{n:importlib.metadata.version(n) for n in ['torch','transformers','lm-format-enforcer']},'study_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 if previous:assert previous['dataset_sha256']==metadata['dataset_sha256'] and previous['study_source_sha256']==metadata['study_source_sha256']
 else:meta_path.write_text(json.dumps(metadata,indent=2))
 f=out/'traces.jsonl';rows=[json.loads(s) for s in f.read_text().splitlines()] if f.exists() else []
 done={(r['condition'],r['task_id']) for r in rows}
 with f.open('a') as handle:
  # Rotate policy order across tasks to reduce fixed-order timing bias.
  for i,t in enumerate(tasks):
   policies=['plain','constrained','recovery'];policies=policies[i%3:]+policies[:i%3]
   for policy in policies:
    if (policy,t['id']) in done:continue
    row=trial(model,t,policy);rows.append(row);handle.write(json.dumps(row)+'\n');handle.flush();print(a.model,policy,t['id'],row['success'],flush=True)
 summary=summarize(rows);(out/'summary.json').write_text(json.dumps(summary,indent=2));print('COMPLETED',len(rows),flush=True)
if __name__=='__main__':main()
