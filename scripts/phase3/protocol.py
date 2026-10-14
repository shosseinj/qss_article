"""Artifact, final-test and resumability gates. No automatic downloads."""
from pathlib import Path
import csv,hashlib,importlib.util,json,re,subprocess
from . import core
ROOT=Path(__file__).resolve().parents[2]

def load_config(path):
 import yaml
 value=yaml.safe_load(Path(path).read_text())
 if not isinstance(value,dict):raise ValueError('Configuration must be a mapping')
 return value

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def source_fingerprint():
 paths=list((ROOT/'scripts/phase3').glob('*.py'))+list((ROOT/'results/phase3/recovery/source/models').glob('*.py'))
 return digest({str(p.relative_to(ROOT)):core.file_hash(p) for p in sorted(paths)})

def resolve(path):
 if not path:return None
 p=Path(path).expanduser();return p if p.is_absolute() else ROOT/p

def run_directory(run_id):
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,100}',run_id) or '..' in run_id:raise ValueError('Unsafe run_id')
 return ROOT/'results/phase3'/run_id

def require_test_lock(config):
 if config.get('stage')!='official_test':return
 p=resolve(config.get('preregistration'))
 if not p or not p.is_file():raise ValueError('Final test requires a frozen preregistration')
 lock=load_config(p)
 if lock.get('status')!='frozen' or lock.get('final_config_sha256')!=digest(config) or lock.get('source_fingerprint')!=source_fingerprint():raise ValueError('Final-test protocol is draft or config/source changed')


def preflight(config):
 blockers=[]
 for key,role in [('checkpoint','checkpoint'),('metadata','checkpoint metadata')]:
  p=resolve(config.get('model',{}).get(key))
  if p is None or not p.is_file():blockers.append('missing '+role)
 manifest=resolve(config.get('data',{}).get('manifest'))
 if manifest is None or not manifest.is_file():blockers.append('missing raw-event manifest/data')
 if not config.get('model',{}).get('checkpoint_sha256'):blockers.append('unknown checkpoint SHA-256')
 if not config.get('model',{}).get('metadata_sha256'):blockers.append('unknown checkpoint metadata SHA-256')
 if not config.get('data',{}).get('manifest_sha256'):blockers.append('unknown manifest SHA-256')
 if not importlib.util.find_spec('torch'):blockers.append('PyTorch unavailable in selected interpreter')
 if not importlib.util.find_spec('numpy'):blockers.append('NumPy unavailable in selected interpreter')
 if config.get('stage')=='official_test':
  try:require_test_lock(config)
  except ValueError as e:blockers.append(str(e))
 return {'status':'blocked_resource' if blockers else 'ready','blockers':blockers,'clean_prediction':None,
  'clean_accuracy':None,'attack_successes':None,'attack_denominator':None,'asr':None,
  'elapsed_search_seconds':None,'peak_memory_bytes':None,'estimated_campaign_seconds':None,
  'evidence_status':None,'experimental_result_count':0,'real_checkpoint_loaded':False,'real_data_loaded':False}

def check_hash(path,expected):
 p=resolve(path)
 if not p or not p.is_file() or not expected or core.file_hash(p)!=expected:raise ValueError('Missing or mismatched artifact hash: '+str(path))
 return p

def read_manifest(path,split):
 with Path(path).open(newline='') as f:rows=list(csv.DictReader(f))
 required={'example_id','label','dataset_split','events_path','events_sha256'}
 if not rows or not required<=set(rows[0]):raise ValueError('Incomplete/empty manifest schema')
 if len({r['example_id'] for r in rows})!=len(rows):raise ValueError('Duplicate manifest IDs')
 if any(r['dataset_split']!=split for r in rows):raise ValueError('Split leakage or mislabeled manifest')
 for r in rows:
  r['label']=int(r['label'])
  if not 0<=r['label']<10:raise ValueError('Invalid class')
 return rows

def require_complete_clean_test(rows,stage):
 if stage=='official_test' and len(rows)!=10000:raise ValueError('Clean official test requires all 10,000 examples; partial test is not complete')

def can_resume(record,config_sha,source_sha,input_sha,checkpoint_sha):
 if record.get('status')!='completed' or any(record.get(k)!=v for k,v in [('config_sha256',config_sha),('source_fingerprint',source_sha),('input_sha256',input_sha),('checkpoint_sha256',checkpoint_sha)]):return False
 artifacts=record.get('artifacts')
 if not artifacts:return False
 return all(resolve(p) and resolve(p).is_file() and core.file_hash(resolve(p))==h for p,h in artifacts.items())

def load_model(config):
 import torch
 from . import torch_ops
 spec=config['model'];p=check_hash(spec['checkpoint'],spec['checkpoint_sha256'])
 metadata=load_config(check_hash(spec['metadata'],spec['metadata_sha256']))
 required={'training_seed','frontend_seed','variant','preprocessing','source_commit','model_id'}
 if not required<=set(metadata) or metadata['variant']!=spec['variant'] or metadata['training_seed']!=spec['training_seed']:raise ValueError('Checkpoint provenance/architecture mismatch')
 if metadata['preprocessing']!={'bins':10,'window':'clean_endpoints_inclusive','cap':255,'frontend_scale':8,'sensor_size':[34,34]}:raise ValueError('Preprocessing mismatch')
 model=torch_ops.build_model(spec['variant'],freeze_frontend=False)
 payload=torch.load(p,map_location='cpu',weights_only=True)
 if not isinstance(payload,dict) or 'model_state' not in payload:raise ValueError('Expected an explicit model_state checkpoint')
 if payload.get('seed')!=spec['training_seed']:raise ValueError('Saved seed is missing or mismatched')
 model.load_state_dict(payload['model_state'],strict=True)
 device=config.get('device','cpu')
 if device.startswith('cuda') and not torch.cuda.is_available():raise RuntimeError('CUDA required by config but unavailable')
 return model.to(device).eval(),metadata

def load_events(row):
 import numpy as np
 with np.load(check_hash(row['events_path'],row['events_sha256']),allow_pickle=False) as z:
  if not {'ids','x','y','p','t','label'}<=set(z.files):raise ValueError('Raw-event NPZ requires explicit ids/x/y/p/t/label')
  if int(z['label'])!=row['label']:raise ValueError('Manifest/raw label mismatch')
  events=core.Events(**{k:tuple(z[k].tolist()) for k in ['ids','x','y','p','t']})
 if not core.validity(events,events,0)['valid']:raise ValueError('Malformed raw events')
 return events

def validate_attack_config(config):
 a=config.get('attack')
 if not a:return
 if a.get('name') not in ['PGD','TEMP'] or a.get('objective') not in ['ce','margin']:raise ValueError('Unknown attack/objective')
 if a['name']=='TEMP' and a['objective']!='margin':raise ValueError('This TEMP implementation optimizes margin only')
 if a['name']=='TEMP':core.temp_schedule(a['requested_Q'])

def environment_fingerprint(env):
 keys=['python','executable','platform','cpu_model','cpu_logical','ram_total_bytes','torch','numpy','cuda_available','cuda_runtime','gpu','vram_bytes','device_uuid','driver_version','determinism','timestamp_dtype','statevector_dtype']
 return digest({k:env.get(k) for k in keys})

def bind_run(out,config,environment):
 p=Path(out)/'run_identity.json'
 identity={'config_sha256':digest(config),'source_fingerprint':source_fingerprint(),'environment_fingerprint':environment_fingerprint(environment)}
 if p.exists():
  if json.loads(p.read_text())!=identity:raise ValueError('Run identity changed (config/source/environment); use a new run_id')
 else:core.atomic_json(p,identity)
 return identity
