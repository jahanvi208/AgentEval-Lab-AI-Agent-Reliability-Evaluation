import json,unittest
from agenteval.study3 import trial
class Fake:
 def __init__(self,*plans):self.plans=iter(plans)
 def generate_plan(self,messages,constrained):return json.dumps(next(self.plans)),0
class StudyTests(unittest.TestCase):
 def test_execution_recovery(self):
  bad={'steps':[{'id':'s1','tool':'calculate','arguments':{'operation':'add','a':'wrong','b':4}}],'answer':{'ref':'s1'}}
  good={'steps':[{'id':'s1','tool':'calculate','arguments':{'operation':'add','a':3,'b':4}}],'answer':{'ref':'s1'}}
  t=dict(id='x',category='arithmetic',prompt='add',expected=7,required_tools=['calculate'])
  self.assertTrue(trial(Fake(bad,good),t,'recovery')['success'])
  self.assertFalse(trial(Fake(bad,good),t,'constrained')['success'])
 def test_budget(self):
  plan={'steps':[{'id':'s1','tool':'calculate','arguments':{'operation':'add','a':3,'b':4}},{'id':'s2','tool':'calculate','arguments':{'operation':'add','a':{'ref':'s1.owner'},'b':4}}],'answer':{'ref':'s2'}}
  t=dict(id='x',category='arithmetic',prompt='add',expected=7,required_tools=['calculate'])
  r=trial(Fake(plan,plan),t,'recovery');self.assertLessEqual(len(r['calls']),3);self.assertFalse(r['success'])
 def test_prohibited(self):
  p={'steps':[{'id':'s1','tool':'run_shell','arguments':{}}],'answer':{'ref':'s1'}}
  t=dict(id='x',category='injection',prompt='x',expected='UNKNOWN',required_tools=[])
  self.assertFalse(trial(Fake(p),t,'plain')['policy_compliant'])
