"""Read-only artifact inventory; missing values are null, not zero measurements."""
from pathlib import Path
import importlib.util,json,os,platform,subprocess,sys
from .core import atomic_json,file_hash
ROOT=Path(__file__).resolve().parents[2]
HIST='80d02f5733d4cbe7c3e69b828dff66d50ba5c211'

def environment():
 result={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
 'cpu_logical':os.cpu_count(),'cpu_model':None,'ram_total_bytes':None,'ram_available_bytes':None,
 'torch':None,'numpy':None,'cuda_available':False,'cuda_runtime':None,'gpu':None,'vram_bytes':None,
 'determinism':None,'device_policy':'cpu development checks; real pilot requires verified artifacts',
 'timestamp_dtype':'float32','statevector_dtype':'complex64','candidate_chunk':64,'examples_per_batch':1}
 if Path('/proc/meminfo').exists():
  mem={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.split()[1].isdigit()}
  result['ram_total_bytes']=mem.get('MemTotal');result['ram_available_bytes']=mem.get('MemAvailable')
 if Path('/proc/cpuinfo').exists():result['cpu_model']=next((x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),None)
 if importlib.util.find_spec('torch'):
  import torch
  result.update(torch=torch.__version__,cuda_available=torch.cuda.is_available(),cuda_runtime=torch.version.cuda,
   determinism={'enabled':torch.are_deterministic_algorithms_enabled(),'num_threads':torch.get_num_threads()})
  if torch.cuda.is_available():result.update(gpu=torch.cuda.get_device_name(0),vram_bytes=torch.cuda.get_device_properties(0).total_memory)
 if importlib.util.find_spec('numpy'):
  import numpy;result['numpy']=numpy.__version__
 return result

def inventory():
 recovered=ROOT/'results/phase3/recovery/source'
 items=[]
 for e in json.loads((ROOT/'data/evidence_manifest.json').read_text()):
  path=ROOT/'data/evidence_source_snapshot'/e['path'];exists=path.is_file()
  sha=file_hash(path) if exists else None
  items.append({'artifact_id':'historical:'+e['path'],'role':'source' if e['path'].endswith('.py') else 'historical_report',
   'path':str(path.relative_to(ROOT)),'exists':exists,'size_bytes':path.stat().st_size if exists else None,'sha256':sha,
   'source_commit':e['commit'],'training_seed':None,'split_id':None,'model_id':None,'compatible_with_current_loader':None,
   'evidence_status':'historical_report_only' if not e['path'].endswith('.py') else 'recovered_artifact',
   'manifest_hash_matches':sha==e['sha256'],'missing_fields':[] if exists else ['file']})
 recovered_manifest=ROOT/'Reports/phase3/recovered-source.json'
 if recovered_manifest.exists():items+=json.loads(recovered_manifest.read_text())
 expected=[
 ('frontend','checkpoints/nmnist_hybrid_qsnn_seed42/v3_wide4_classical_full_best.pt','frontend_checkpoint'),
 ('qsnn_seed42','checkpoints/nmnist_hybrid_qsnn_seed42/nmnist_qsnn_v3_multiseed/seed42_best.pt','victim_checkpoint'),
 ('snn_seed42','checkpoints/nmnist_snn_clean_seed42_best.pt','victim_checkpoint'),
 ('split','results/nmnist_snn_multiseed_split.json','training_validation_split'),
 ('timestamp_manifest','results/nmnist_attack_protocol_v3_auditable_seed42/common_clean_correct_manifest.json','attack_manifest'),
 ('legacy_manifest','results/nmnist_common_attack_protocol_seed42/common_clean_correct_manifest.json','attack_manifest'),
 ('budget_defs','results/nmnist_budget_matched_comparison_v2_seed42/budget_definitions.json','run_config'),
 ('calibration','results/nmnist_budget_matched_comparison_v2_seed42/wallclock_calibration.json','timing_arrays'),
 ('per_example','results/nmnist_budget_matched_comparison_v2_seed42/per_sample_results.csv','per_example_records'),
 ('raw_events','data/nmnist','dataset'),
 ('grid_configs','Reports/results/nmnist_controlled_four_models_lr1e4','grid_run_artifacts')]
 for ident,path,role in expected:
  local=ROOT/path;snapshot=ROOT/'data/evidence_source_snapshot'/path
  actual=local if local.exists() else snapshot
  exists=actual.exists()
  items.append({'artifact_id':ident,'role':role,'path':path,'exists':exists,'size_bytes':actual.stat().st_size if actual.is_file() else None,
   'sha256':file_hash(actual) if actual.is_file() else None,'source_commit':HIST,'training_seed':None,'split_id':None,'model_id':None,
   'compatible_with_current_loader':None,'evidence_status':'recovered_artifact' if exists else 'historical_report_only',
   'missing_fields':['checkpoint metadata validation'] if exists and 'checkpoint' in role else [] if exists else ['file','metadata'],
   'path_basis':'literal historical runner/report reference; not a recovered artifact'})
 files=[str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and p.suffix.lower() in ['.pt','.pth','.npz','.npy','.parquet']]
 repo_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 sources={str(p.relative_to(ROOT)):file_hash(p) for base in ['scripts/phase3','configs/phase3'] for p in (ROOT/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
 tree=json.loads((ROOT/'Reports/phase3/historical-tree.json').read_text())
 tree_artifacts=[x['path'] for x in tree.get('tree',[]) if x['path'].lower().endswith(('.pt','.pth','.npz','.parquet'))]
 out={'local_git_commit':repo_commit,'historical_source_commit':HIST,'worktree_dirty':True,'source_hashes':sources,
 'environment':environment(),'artifacts':items,'local_candidate_artifact_files':files,'public_pinned_tree_artifacts':tree_artifacts,
 'search_scope':['workspace recursive','referenced paths','Downloads/QSNN_Overleaf*.zip (listing only)','Documents/Downloads/Desktop checkpoint filenames','pinned public GitHub tree'],
 'checkpoint_compatibility':'not assessed: no actual checkpoint exists','dataset_availability':'absent',
 'discrepancies':['Git commit predates uncommitted Phase2; current code hashes are required in every new run',
  'Public recovery provides missing loader/model source but no historical weights or raw data',
  'Historical requirements specify torch 2.9.1; Phase2 environment note observed 2.5.1. Neither proves all historical run versions. Current CPU environment is a separate new configuration.']}
 atomic_json(ROOT/'Reports/phase3/inventory.json',out);atomic_json(ROOT/'Reports/phase3/environment.json',out['environment'])
 return out

if __name__=='__main__':
 out=inventory();print('Inventoried',len(out['artifacts']),'entries; checkpoints/data:',out['local_candidate_artifact_files'])
