"""Loopback API and UI. BareBones Projects, Designed by: Justin Levesque-Welsch."""
import json, os, secrets, sys, urllib.request, urllib.error
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from .core import *
ROOT=Path(__file__).resolve().parent.parent
WEB=ROOT/'web'
HOST='127.0.0.1';PORT=int(os.getenv('OMARCHY_SKILL_PORT','8765'))
# API keys stay outside the database and are never returned to browsers.

def api_chat(provider, model, message):
 if not message or len(message)>20000:raise ValueError('Message size invalid')
 if provider=='ollama':
  endpoint='http://127.0.0.1:11434/api/chat'
  payload={'model':model or 'llama3.2','messages':[{'role':'user','content':message}],'stream':False}
  headers={'Content-Type':'application/json'}
 elif provider=='openai':
  endpoint='https://api.openai.com/v1/chat/completions'
  key=os.getenv('OPENAI_API_KEY','')
  if not key:raise ValueError('OPENAI_API_KEY is not set in the service environment')
  payload={'model':model or 'gpt-4.1-mini','messages':[{'role':'user','content':message}]}
  headers={'Content-Type':'application/json','Authorization':'Bearer '+key}
 elif provider=='anthropic':
  endpoint='https://api.anthropic.com/v1/messages'
  key=os.getenv('ANTHROPIC_API_KEY','')
  if not key:raise ValueError('ANTHROPIC_API_KEY is not set in the service environment')
  payload={'model':model or 'claude-sonnet-4-5','max_tokens':1024,'messages':[{'role':'user','content':message}]}
  headers={'Content-Type':'application/json','x-api-key':key,'anthropic-version':'2023-06-01'}
 else:raise ValueError('Unsupported provider')
 req=urllib.request.Request(endpoint,data=json.dumps(payload).encode(),headers=headers,method='POST')
 with urllib.request.urlopen(req,timeout=90) as response:result=json.load(response)
 if provider=='anthropic':return ''.join(part.get('text','') for part in result.get('content',[]))
 if provider=='ollama':return result.get('message',{}).get('content','')
 return result['choices'][0]['message']['content']

class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(WEB),**kw)
 def _json(self,code,payload):
  raw=json.dumps(payload).encode();self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def _read(self):
  n=int(self.headers.get('Content-Length','0'))
  if n>250000:raise ValueError('Payload too large')
  return json.loads(self.rfile.read(n) or b'{}')
 def _same_origin(self):
  origin=self.headers.get('Origin')
  return not origin or origin==f'http://{HOST}:{PORT}'
 def do_GET(self):
  p=urlsplit(self.path)
  if p.path=='/api/skills':return self._json(200,{'skills':list_skills(parse_qs(p.query).get('q',[''])[0])})
  if p.path=='/api/status':return self._json(200,{'agents':list(KNOWN_AGENTS),'provider':get_setting('provider','ollama'),'model':get_setting('model','llama3.2')})
  if p.path.startswith('/api/'):return self._json(404,{'error':'Not found'})
  return super().do_GET()
 def do_POST(self):
  if not self._same_origin():return self._json(403,{'error':'Cross-origin requests denied'})
  try:
   p=urlsplit(self.path).path; data=self._read()
   if p=='/api/skills':result={'id':create_skill(data['title'],data['content'],data.get('agents'))}
   elif p=='/api/skill/update':
    update_skill(data['id'],data.get('enabled'),data.get('agents'));result={'ok':True}
   elif p=='/api/skill/delete':delete_skill(data['id']);result={'ok':True}
   elif p=='/api/sync':result={'results':sync(confirm=data.get('confirm') is True)}
   elif p=='/api/settings':
    for key in ('provider','model'):
     if key in data:set_setting(key,data[key])
    result={'ok':True}
   elif p=='/api/chat':result={'reply':api_chat(get_setting('provider','ollama'),get_setting('model','llama3.2'),str(data['message']))}
   else:return self._json(404,{'error':'Not found'})
   return self._json(200,result)
  except (ValueError,KeyError,PermissionError,sqlite3.IntegrityError) as e:return self._json(400,{'error':str(e)})
  except urllib.error.HTTPError as e:return self._json(502,{'error':f'Provider returned HTTP {e.code}'})
  except Exception as e:
   print('Request error:',repr(e),file=sys.stderr);return self._json(500,{'error':'Internal error; see service logs'})
 def log_message(self,fmt,*args):print(fmt%args,file=sys.stderr)

def main():
 dbconnect().close();print(f'Omarchy Skill Hub on http://{HOST}:{PORT}',file=sys.stderr)
 ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
if __name__=='__main__':main()
