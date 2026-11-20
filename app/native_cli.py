"""Native Omarchy panel bridge. No shell commands, no remote listener."""
import json, os, re, sys
from pathlib import Path
from . import core

CONFIG = Path(os.getenv('XDG_CONFIG_HOME',Path.home()/'.config'))/'omarchy-skill-hub'
CONFIG_FILE=CONFIG/'config.json'
MCP_FILE=CONFIG/'mcp.json'
VALID_THEME={'auto','dark','light'}
PROVIDERS={'ollama','openai','anthropic'}

def read_json(path,default):
 if not path.is_file():return default
 data=json.loads(path.read_text(encoding='utf8'))
 if not isinstance(data,dict):raise ValueError('Invalid configuration object')
 return data

def write_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n',encoding='utf8');tmp.chmod(0o600);tmp.replace(path)

def config():
 value=read_json(CONFIG_FILE,{})
 return {'theme':value.get('theme','auto'),'defaultAgent':value.get('defaultAgent','All')}

def mcp_list():
 raw=read_json(MCP_FILE,{'mcpServers':{}})
 servers=raw.get('mcpServers',{})
 if not isinstance(servers,dict):raise ValueError('Invalid MCP server list')
 return {'servers':[{'name':k,'type':str(v.get('type','stdio')) if isinstance(v,dict) else 'invalid','configured':True} for k,v in sorted(servers.items())][:80]}

def load_provider_env():
 """Parse a tiny env file without evaluating shell code or printing secrets."""
 path = CONFIG/'provider.env'
 if not path.is_file():return
 if path.stat().st_mode & 0o077:raise ValueError('provider.env must be chmod 600')
 for line in path.read_text(encoding='utf8').splitlines():
  stripped=line.strip()
  if not stripped or stripped.startswith('#'):continue
  key,sep,value=stripped.partition('=')
  if sep and key in ('OPENAI_API_KEY','ANTHROPIC_API_KEY'):
   os.environ.setdefault(key,value.strip().strip('"').strip("'"))

def main(argv):
 if not argv:raise ValueError('A command is required')
 action,*args=argv
 if action=='rpc':
  envelope=json.loads(sys.stdin.readline(256000))
  params=envelope.get('args') if isinstance(envelope,dict) else None
  if not isinstance(params,list) or not params or params[0]=='rpc' or len(params)>6 or any(not isinstance(x,str) for x in params):
   raise ValueError('Invalid RPC arguments')
  if len(json.dumps(params))>210000:raise ValueError('RPC request too large')
  return main(params)
 if action=='skills': result={'skills':[{k:s[k] for k in ('id','title','slug','enabled','agents')} for s in core.list_skills()]}
 elif action=='status':result={'agents':list(core.KNOWN_AGENTS),'provider':core.get_setting('provider','ollama'),'model':core.get_setting('model','llama3.2'),'config':config()}
 elif action=='mcp':result=mcp_list()
 elif action=='create':
  if len(args)!=3:raise ValueError('create requires title content agent')
  result={'id':core.create_skill(args[0],args[1],[args[2]])}
 elif action=='toggle':
  if len(args)!=2 or args[1] not in ('true','false'):raise ValueError('Invalid toggle')
  core.update_skill(args[0],enabled=args[1]=='true');result={'ok':True}
 elif action=='assign':
  if len(args)!=2:raise ValueError('assign requires id and agent')
  core.update_skill(args[0],agents=[args[1]]);result={'ok':True}
 elif action=='sync':
  if args!=['--confirm']:raise ValueError('Sync requires explicit confirmation')
  result={'results':core.sync(confirm=True)}
 elif action=='provider-set':
  if len(args)!=2 or args[0] not in PROVIDERS or not 1<=len(args[1])<=100:raise ValueError('Invalid provider configuration')
  core.set_setting('provider',args[0]);core.set_setting('model',args[1]);result={'ok':True}
 elif action=='config-set':
  if len(args)!=2:raise ValueError('config-set expects key value')
  key,value=args;data=config()
  if key=='theme' and value in VALID_THEME:data['theme']=value
  elif key=='defaultAgent' and (value=='All' or value in core.KNOWN_AGENTS):data['defaultAgent']=value
  else:raise ValueError('Unsupported config setting')
  write_json(CONFIG_FILE,data);result={'config':data}
 elif action=='mcp-add':
  if len(args)!=3:raise ValueError('mcp-add expects name type executable-or-url')
  name,typ,target=args
  if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}',name):raise ValueError('Invalid MCP name')
  if typ=='stdio':
   if not target.startswith('/') or not Path(target).is_file():raise ValueError('MCP stdio command must be an existing absolute executable path')
   entry={'type':'stdio','command':target,'args':[]}
  elif typ=='streamable-http':
   if not target.startswith('https://') or len(target)>2048:raise ValueError('Remote MCP requires HTTPS')
   entry={'type':'streamable-http','url':target}
  else:raise ValueError('Unsupported MCP transport')
  m=read_json(MCP_FILE,{'mcpServers':{}});m.setdefault('mcpServers',{})[name]=entry;write_json(MCP_FILE,m)
  result={'ok':True,'note':'Saved to Skill Hub MCP catalog. Provider configuration requires explicit separate setup.'}
 elif action=='chat':
  if len(args)!=1:raise ValueError('chat expects message')
  load_provider_env()
  from .server import api_chat
  result={'reply':api_chat(core.get_setting('provider','ollama'),core.get_setting('model','llama3.2'),args[0])[:8000]}
 else:raise ValueError('Unknown command')
 print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':
 try:main(sys.argv[1:])
 except (ValueError,KeyError,OSError,json.JSONDecodeError) as e:
  print(json.dumps({'error':str(e)}),file=sys.stderr);sys.exit(2)
