import json, os, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class MarketplaceTest(unittest.TestCase):
    def test_manifest_and_widget(self):
        m=json.loads((ROOT/'manifest.json').read_text())
        self.assertEqual(m['schemaVersion'],1)
        self.assertEqual(m['id'],'barebones.skill-hub')
        self.assertIn('bar-widget',m['kinds'])
        self.assertTrue((ROOT/m['entryPoints']['barWidget']).is_file())
        self.assertEqual(m['barWidget']['defaultSection'],'right')
        qml=(ROOT/'Widget.qml').read_text()
        self.assertIn('Qt.openUrlExternally',qml)
    def test_user_install_and_remove_are_isolated(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)/'home';home.mkdir()
            bindir=Path(tmp)/'fakebin';bindir.mkdir()
            log=Path(tmp)/'systemctl.log'
            exe=bindir/'systemctl'
            exe.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$TEST_SYSTEMCTL_LOG"\n')
            exe.chmod(0o755)
            env=os.environ.copy();env.update(HOME=str(home), XDG_DATA_HOME=str(home/'.local/share'), XDG_CONFIG_HOME=str(home/'.config'),PATH=f'{bindir}:'+os.environ['PATH'],TEST_SYSTEMCTL_LOG=str(log))
            subprocess.run(['bash',str(ROOT/'bin/install.sh')],check=True,env=env,capture_output=True)
            self.assertFalse((home/'.config/systemd/user/omarchy-skill-hub.service').exists())
            self.assertTrue((home/'.local/share/omarchy-skill-hub/runtime/app/server.py').exists())
            self.assertTrue((home/'.local/share/applications/omarchy-skill-hub.desktop').exists())
            self.assertTrue((home/'.local/bin/omarchy-skill-hub').exists())
            self.assertNotIn('enable --now omarchy-skill-hub.service',log.read_text() if log.exists() else '')
            self.assertTrue((home/'.local/bin/omarchy-skill-hubctl').exists())
            self.assertIn('omarchy-shell shell summon', (home/'.local/bin/omarchy-skill-hub').read_text())
            # Preserve unrelated user content on uninstall.
            saved=home/'.config/omarchy-skill-hub/provider.env';saved.parent.mkdir(exist_ok=True);saved.write_text('LOCAL_ONLY=1')
            subprocess.run(['bash',str(ROOT/'bin/uninstall.sh')],check=True,env=env,capture_output=True)
            self.assertTrue(saved.exists())
            self.assertFalse((home/'.config/systemd/user/omarchy-skill-hub.service').exists())
            self.assertFalse((home/'.local/bin/omarchy-skill-hub').exists())
            self.assertFalse((home/'.local/bin/omarchy-skill-hubctl').exists())
if __name__=='__main__': unittest.main()
