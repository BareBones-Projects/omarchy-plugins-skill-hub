"""BareBones Projects, Designed by: Justin Levesque-Welsch."""
import tempfile,unittest
from pathlib import Path
from app.core import create_skill, list_skills, update_skill, delete_skill, skill_markdown, valid_slug
class SkillsTest(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.db=Path(self.tmp.name)/'x.db'
 def tearDown(self):self.tmp.cleanup()
 def test_lifecycle(self):
  sid=create_skill('Traffic Routing','Respect lanes',['Codex'],self.db)
  s=list_skills(path=self.db)[0];self.assertEqual(s['slug'],'traffic-routing');self.assertEqual(s['agents'],['Codex'])
  self.assertIn('name: traffic-routing',skill_markdown(s))
  update_skill(sid,enabled=False,agents=['All'],path=self.db)
  self.assertFalse(list_skills(path=self.db)[0]['enabled']);self.assertEqual(list_skills(path=self.db)[0]['agents'],['All'])
  delete_skill(sid,self.db);self.assertEqual(list_skills(path=self.db),[])
 def test_reject_invalid(self):
  with self.assertRaises(ValueError):valid_slug('---')
  with self.assertRaises(ValueError):create_skill('Test','',path=self.db)
  with self.assertRaises(ValueError):create_skill('Test','ok',['Unknown Agent'],self.db)
 if __name__=='__main__':unittest.main()
