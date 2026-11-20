"""Native popup backend regression tests."""
import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class NativeCliTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
  self.home=Path(self.tmp.name); (self.home/'data').mkdir();(self.home/'config').mkdir()
  self.env=os.environ.copy();self.env.update(HOME=str(self.home),XDG_DATA_HOME=str(self.home/'data'),XDG_CONFIG_HOME=str(self.home/'config'),PYTHONPATH=str(ROOT))
 def cli(self,*args):
  return subprocess.run([sys.executable,'-m','app.native_cli',*args],env=self.env,capture_output=True,text=True,cwd=ROOT)
 def test_skills_create_status_assign(self):
  r=self.cli('create','New Skill','Only harmless actions','Codex');self.assertEqual(r.returncode,0,r.stderr)
  skill=json.loads(self.cli('skills').stdout)['skills'][0];self.assertEqual(skill['agents'],['Codex'])
  self.assertEqual(self.cli('toggle',skill['id'],'false').returncode,0)
  self.assertEqual(json.loads(self.cli('skills').stdout)['skills'][0]['enabled'],0)
  self.assertEqual(self.cli('assign',skill['id'],'All').returncode,0)
  self.assertEqual(json.loads(self.cli('skills').stdout)['skills'][0]['agents'],['All'])
 def test_mcp_config_and_reject_bad_names(self):
  self.assertNotEqual(self.cli('mcp-add','bad name','stdio','command').returncode,0)
  self.assertEqual(self.cli('mcp-add','local-tool','stdio','/usr/bin/true').returncode,0)
  val=json.loads(self.cli('mcp').stdout)
  self.assertEqual(val['servers'][0]['name'],'local-tool')
  self.assertNotIn('token',json.dumps(val).lower())
 def test_config_provider_and_paths(self):
  self.assertEqual(self.cli('config-set','theme','auto').returncode,0)
  self.assertNotEqual(self.cli('config-set','theme','rainbow').returncode,0)
  config=json.loads(self.cli('status').stdout)['config'];self.assertEqual(config['theme'],'auto')
  self.assertEqual(self.cli('provider-set','ollama','llama3.2').returncode,0)
 def test_sync_requires_explicit_ack(self):
  self.assertNotEqual(self.cli('sync').returncode,0)
 def test_rpc_uses_stdin_instead_of_process_arguments(self):
  import json
  payload=json.dumps({'args':['create','Secret Skill','Do not reveal text','All']})+'\n'
  r=subprocess.run([sys.executable,'-m','app.native_cli','rpc'],input=payload,env=self.env,capture_output=True,text=True,cwd=ROOT)
  self.assertEqual(r.returncode,0,r.stderr)
  self.assertEqual(json.loads(self.cli('skills').stdout)['skills'][0]['title'],'Secret Skill')
 def test_artifacts_natively_open_panel(self):
  manifest=json.loads((ROOT/'manifest.json').read_text());self.assertEqual(manifest['entryPoints']['barWidget'],'BarWidget.qml')
  widget=(ROOT/'BarWidget.qml').read_text();self.assertIn('root.toggle()',widget);self.assertNotIn('openUrlExternally',widget)
  panel=(ROOT/'Panel.qml').read_text();self.assertIn('KeyboardPanel',panel);self.assertIn('Commons.Color',panel)
  self.assertIn('focusTarget: popup.loadedContent',panel)
  self.assertIn('popup.loadedContent.contentHeightHint',panel)
  self.assertIn('stdinEnabled: true',panel)
  self.assertNotIn('cli.command = [bridge].concat(args)',panel)
  installer=(ROOT/'bin/install.sh').read_text();self.assertIn('omarchy-skill-hub.desktop',installer)

if __name__=='__main__':unittest.main()
