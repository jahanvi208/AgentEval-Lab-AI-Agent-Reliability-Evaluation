import json
import unittest
from agenteval.dataset import build,fingerprint
from agenteval.engine import parse_action,equal_answer,run_task
from agenteval.models import ScriptedModel
from agenteval.tools import execute,ToolError
from agenteval.reporting import wilson,summarize

class Fixed:
    def __init__(self,*actions):self.actions=iter(actions)
    def generate(self,messages):return next(self.actions),0

class CoreTests(unittest.TestCase):
    def test_dataset(self):
        tasks=build()
        self.assertEqual(len(tasks),60);self.assertEqual(len({t['id'] for t in tasks}),60)
        self.assertEqual(sum(t['split']=='dev' for t in tasks),15)
        self.assertEqual(fingerprint(tasks),fingerprint(build()))
        self.assertFalse({t['prompt'] for t in tasks if t['split']=='dev'} & {t['prompt'] for t in tasks if t['split']=='test'})
    def test_tools(self):
        self.assertEqual(execute('calculate',{'operation':'divide','a':7,'b':2}),3.5)
        for name,args in [('delete_project',{}),('lookup',{'project_id':'PRJ-999'}),('calculate',{'operation':'divide','a':1,'b':0}),('calculate',{'operation':'add','a':True,'b':2}),('lookup',{'project_id':'PRJ-101','extra':1})]:
            with self.assertRaises(ToolError):execute(name,args)
    def test_protocol(self):
        for raw in ['[]','{"final": true}','{"final":NaN}','```json\n{}\n```','{"final":2,"tool":"x"}']:
            with self.assertRaises(ValueError):parse_action(raw)
    def test_no_boolean_numeric_credit(self):
        self.assertFalse(equal_answer(True,1));self.assertTrue(equal_answer(.3333333,1/3))
    def test_wrong_answer(self):
        task={'id':'x','category':'lookup','prompt':'owner','expected':'Mira','required_tools':['lookup']}
        r=run_task(Fixed('{"final":"Mira"}'),task,'baseline')
        self.assertFalse(r['success']);self.assertEqual(r['failure'],'missing_required_tool')
    def test_feedback_recovers(self):
        task={'id':'x','category':'arithmetic','prompt':'2 plus 2','expected':4,'required_tools':['calculate']}
        actions=['bad','{"tool":"calculate","arguments":{"operation":"add","a":2,"b":2}}','{"final":4}']
        self.assertTrue(run_task(Fixed(*actions),task,'feedback')['success'])
        self.assertFalse(run_task(Fixed(*actions),task,'structured')['success'])
    def test_unsafe_attempt_not_erased(self):
        task={'id':'x','category':'injection','prompt':'x','expected':'UNKNOWN','required_tools':[]}
        r=run_task(Fixed('{"tool":"run_shell","arguments":{}}','{"final":"UNKNOWN"}'),task,'feedback')
        self.assertFalse(r['success']);self.assertFalse(r['policy_compliant'])
    def test_step_limit(self):
        task={'id':'x','category':'lookup','prompt':'x','expected':1,'required_tools':[]}
        r=run_task(Fixed(*['{"tool":"lookup","arguments":{"project_id":"PRJ-101"}}']*2),task,'feedback',2)
        self.assertEqual(r['failure'],'no_final')
    def test_scripted_harness(self):
        rows=[run_task(ScriptedModel(),t,'feedback') for t in build()]
        self.assertTrue(all(r['success'] for r in rows))
        self.assertEqual(summarize(rows)['feedback']['tasks'],60)
    def test_wilson(self):
        lo,hi=wilson(0,10);self.assertEqual(lo,0);self.assertGreater(hi,0)
        lo,hi=wilson(10,10);self.assertLess(lo,1);self.assertEqual(hi,1)

if __name__=='__main__':unittest.main()
