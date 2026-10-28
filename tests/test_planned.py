import unittest,json
from agenteval.planned import parse_plan,run_planned
from test_core import Fixed
class PlanTests(unittest.TestCase):
 def test_forward_reference(self):
  with self.assertRaises(ValueError):parse_plan('{"steps":[],"answer":{"ref":"s1"}}')
 def test_forbidden_tool(self):
  with self.assertRaises(ValueError):parse_plan('{"steps":[{"id":"s1","tool":"run_shell","arguments":{}}],"answer":{"ref":"s1"}}')
 def test_no_literal_guesses(self):
  with self.assertRaises(ValueError):parse_plan('{"steps":[],"answer":12000}')
 def test_multistep(self):
  p={'steps':[{'id':'s1','tool':'lookup','arguments':{'project_id':'PRJ-101'}},{'id':'s2','tool':'calculate','arguments':{'operation':'subtract','a':{'ref':'s1.budget'},'b':{'ref':'s1.spent'}}}],'answer':{'ref':'s2'}}
  t={'id':'x','category':'multistep','prompt':'remaining','expected':3600,'required_tools':['lookup','calculate']}
  self.assertTrue(run_planned(Fixed(json.dumps(p)),t)['success'])
 def test_unknown_is_not_success_for_known_answer(self):
  t={'id':'x','category':'lookup','prompt':'owner','expected':'Mira','required_tools':['lookup']}
  self.assertFalse(run_planned(Fixed('{"steps":[],"answer":"UNKNOWN"}'),t)['success'])
