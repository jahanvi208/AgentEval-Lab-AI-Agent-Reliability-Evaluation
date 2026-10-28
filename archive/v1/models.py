"""Local Transformers inference and explicitly labelled scripted harness smoke backend."""
import json
import re

class ScriptedModel:
    kind='scripted_smoke'
    model_id='scripted-smoke-not-an-LLM'
    revision=None
    def generate(self,messages):
        prompt=messages[1]['content']
        observations=[]
        for m in messages[2:]:
            if m['role']=='user' and m['content'].startswith('Tool observation: '):
                observations.append(json.loads(m['content'][18:]))
        if observations and 'error' in observations[-1]:
            return json.dumps({'final':'UNKNOWN'}),0
        if 'unnamed' in prompt:
            result={'final':'UNKNOWN'}
        elif 'PRJ-' in prompt:
            key=re.search(r'PRJ-\d+',prompt).group()
            if not observations:
                result={'tool':'lookup','arguments':{'project_id':key}}
            elif len(observations)==1:
                record=observations[0]['result']
                if 'minus spent' in prompt or 'divided by budget' in prompt or 'twice' in prompt:
                    op,a,b=('subtract',record['budget'],record['spent']) if 'minus spent' in prompt else ('divide',record['spent'],record['budget']) if 'divided by budget' in prompt else ('multiply',record['budget'],2)
                    result={'tool':'calculate','arguments':{'operation':op,'a':a,'b':b}}
                else:
                    field='status' if 'status' in prompt else 'budget' if 'budget' in prompt else 'owner'
                    result={'final':record[field]}
            else: result={'final':observations[-1]['result']}
        elif observations: result={'final':observations[-1]['result']}
        else:
            a,word,b=re.search(r'(\d+) (plus|minus|times|divided by) (\d+|zero)',prompt).groups()
            result={'tool':'calculate','arguments':{'operation':{'plus':'add','minus':'subtract','times':'multiply','divided by':'divide'}[word],'a':int(a),'b':0 if b=='zero' else int(b)}}
        return json.dumps(result),0

class HFModel:
    kind='huggingface_local'
    def __init__(self,model_id,revision=None,max_new_tokens=160,device='cpu'):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
        set_seed(42)
        self.model_id=model_id;self.max_new_tokens=max_new_tokens
        self.tokenizer=AutoTokenizer.from_pretrained(model_id,revision=revision,trust_remote_code=False)
        self.model=AutoModelForCausalLM.from_pretrained(model_id,revision=revision,trust_remote_code=False,dtype=torch.float32).to(device).eval()
        self.revision=getattr(self.model.config,'_commit_hash',revision)
        self.device=device
    def generate(self,messages):
        import torch
        text=self.tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        inputs=self.tokenizer(text,return_tensors='pt',add_special_tokens=False).to(self.device)
        if inputs['input_ids'].shape[1]+self.max_new_tokens>8192:
            raise RuntimeError('Context exceeds experiment limit; reduce max steps or prompt length')
        with torch.inference_mode():
            out=self.model.generate(**inputs,max_new_tokens=self.max_new_tokens,do_sample=False,pad_token_id=self.tokenizer.eos_token_id)
        generated=out[0,inputs['input_ids'].shape[1]:]
        return self.tokenizer.decode(generated,skip_special_tokens=True),len(generated)
