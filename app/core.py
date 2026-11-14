"""Omarchy Skill Hub core. BareBones Projects, Designed by: Justin Levesque-Welsch."""
import json, os, re, shutil, sqlite3, uuid
from pathlib import Path
from datetime import datetime, timezone

APP_DIR = Path(os.getenv('XDG_DATA_HOME', Path.home()/'.local/share'))/'omarchy-skill-hub'
CONFIG_DIR = Path(os.getenv('XDG_CONFIG_HOME', Path.home()/'.config'))/'omarchy-skill-hub'
DB = APP_DIR/'skills.sqlite3'
KNOWN_AGENTS = {
 'Claude Code': Path.home()/'.claude/skills',
 'Codex': Path.home()/'.agents/skills',
 'OpenCode': Path.home()/'.config/opencode/skills',
 'Gemini CLI': Path.home()/'.gemini/skills',
}
NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

def dbconnect(path=DB):
 path.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(path);c.row_factory=sqlite3.Row
 c.executescript('''CREATE TABLE IF NOT EXISTS skills (id TEXT PRIMARY KEY, slug TEXT UNIQUE NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, created TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS assignments(skill_id TEXT NOT NULL, agent TEXT NOT NULL, PRIMARY KEY(skill_id, agent), FOREIGN KEY(skill_id) REFERENCES skills(id));
 CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);''')
 return c

def valid_slug(title):
 s=re.sub(r'[^a-z0-9]+','-',title.lower()).strip('-')
 if not NAME.fullmatch(s) or len(s)>64:raise ValueError('Invalid skill name (1-64 lowercase letters, numbers or hyphens)')
 return s

def create_skill(title, text, agents=None, path=DB):
 title=title.strip(); text=text.strip(); slug=valid_slug(title)
 if not text or len(text)>200000:raise ValueError('Skill content must contain 1-200000 characters')
 agents=agents or ['All']
 if any(x!='All' and x not in KNOWN_AGENTS for x in agents):raise ValueError('Unknown agent')
 skill_id=str(uuid.uuid4()); created=datetime.now(timezone.utc).isoformat()
 with dbconnect(path) as c:
  c.execute('INSERT INTO skills VALUES (?,?,?,?,?,?)',(skill_id,slug,title,text,1,created))
  c.executemany('INSERT INTO assignments VALUES (?,?)',[(skill_id,x) for x in set(agents)])
 return skill_id

def list_skills(search='',path=DB):
 with dbconnect(path) as c:
  rows=c.execute('SELECT * FROM skills WHERE title LIKE ? OR content LIKE ? ORDER BY title',('%'+search+'%','%'+search+'%')).fetchall()
  return [dict(r)|{'agents':[a[0] for a in c.execute('SELECT agent FROM assignments WHERE skill_id=?',(r['id'],))]} for r in rows]

def update_skill(skill_id,enabled=None,agents=None,path=DB):
 with dbconnect(path) as c:
  if c.execute('SELECT 1 FROM skills WHERE id=?',(skill_id,)).fetchone() is None:raise KeyError('Skill not found')
  if enabled is not None:c.execute('UPDATE skills SET enabled=? WHERE id=?',(int(bool(enabled)),skill_id))
  if agents is not None:
   if not isinstance(agents,list) or any(x!='All' and x not in KNOWN_AGENTS for x in agents):raise ValueError('Unknown agent')
   c.execute('DELETE FROM assignments WHERE skill_id=?',(skill_id,))
   c.executemany('INSERT INTO assignments VALUES (?,?)',[(skill_id,x) for x in set(agents)])

def delete_skill(skill_id,path=DB):
 with dbconnect(path) as c:
  c.execute('DELETE FROM assignments WHERE skill_id=?',(skill_id,));c.execute('DELETE FROM skills WHERE id=?',(skill_id,))

def safe_frontmatter(value):return json.dumps(value,ensure_ascii=False)

def skill_markdown(skill):
 text=skill['content']
 if text.startswith('---\n') and '\n---\n' in text[4:]:return text
 return f'---\nname: {skill["slug"]}\ndescription: {safe_frontmatter("Use when the user asks for " + skill["title"])}\n---\n\n{text}\n'

def sync(path=DB,confirm=False):
 """Copies only app-managed files; never deletes unmanaged agent skills."""
 if not confirm:raise PermissionError('Sync requires explicit confirmation')
 skills=list_skills(path=path); results=[]
 for agent,folder in KNOWN_AGENTS.items():
  for skill in skills:
   target=folder/skill['slug']/'SKILL.md'
   owned=target.parent/'.omarchy-skill-hub'
   assigned='All' in skill['agents'] or agent in skill['agents']
   desired=bool(skill['enabled']) and assigned
   if desired:
    if target.exists() and not owned.exists():results.append({'agent':agent,'skill':skill['slug'],'status':'conflict'});continue
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(skill_markdown(skill),encoding='utf8');owned.write_text(skill['id'])
    results.append({'agent':agent,'skill':skill['slug'],'status':'installed'})
   elif owned.exists() and owned.read_text().strip()==skill['id']:
    target.unlink(missing_ok=True);owned.unlink(missing_ok=True)
    try:target.parent.rmdir()
    except OSError:pass
    results.append({'agent':agent,'skill':skill['slug'],'status':'removed'})
 # Clean up orphaned files from skills deleted in the Hub, but only when marked as Hub-owned.
 live_ids={s['id'] for s in skills}
 for agent,folder in KNOWN_AGENTS.items():
  if not folder.exists():continue
  for owned in folder.glob('*/.omarchy-skill-hub'):
   try:
    stored=owned.read_text().strip()
    if stored in live_ids:continue
    target=owned.parent/'SKILL.md'
    target.unlink(missing_ok=True);owned.unlink(missing_ok=True)
    try:owned.parent.rmdir()
    except OSError:pass
    results.append({'agent':agent,'skill':owned.parent.name,'status':'removed-deleted'})
   except OSError:continue
 return results

def get_setting(key, default='', path=DB):
 with dbconnect(path) as c:
  r=c.execute('SELECT value FROM settings WHERE key=?',(key,)).fetchone();return r[0] if r else default

def set_setting(key,value,path=DB):
 if key not in ('provider','model','endpoint'):raise ValueError('Unknown setting')
 with dbconnect(path) as c:c.execute('INSERT INTO settings VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,str(value)))
