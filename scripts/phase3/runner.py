"""Artifact-gated pilot and versioned attacks. Scientific results require actual files.

NPZ events and checkpoint metadata are hashed before model/data use. Synthetic
fixtures are confined to tests. Missing prerequisites produce null metrics.
"""
from pathlib import Path
import argparse,csv,hashlib,itertools,json,resource,subprocess,time
from . import core,protocol
from .inventory import environment,inventory
ROOT=protocol.ROOT

def write_jsonl(path,rows):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp')
 with tmp.open('w') as f:
  for row in rows:f.write(json.dumps(row,sort_keys=True,allow_nan=False)+'\n')
 tmp.replace(p)

class WithLogits:
 def __init__(self,bank,logits):self.bank=bank;self.logits=logits
 def __len__(self):return len(self.bank)
 def __iter__(self):
  for i,c in enumerate(self.bank):yield core.Candidate(c.index,c.events,self.logits[i])

def configure(config):
 import torch
 torch.set_num_threads(int(config.get('cpu_threads',2)))
 torch.manual_seed(int(config.get('model',{}).get('training_seed') or 42))
 torch.use_deterministic_algorithms(bool(config.get('deterministic',True)))
 if torch.cuda.is_available():torch.cuda.manual_seed_all(int(config.get('attack',{}).get('seed',42)))

def inputs(config):
 protocol.require_test_lock(config)
 p=protocol.check_hash(config['data']['manifest'],config['data']['manifest_sha256'])
 return protocol.read_manifest(p,'official_test' if config['stage']=='official_test' else 'validation')

class WithFallback:
 def __init__(self,bank,clean):self.bank=bank;self.clean=clean
 def __len__(self):return len(self.bank)+1
 def __iter__(self):return itertools.chain([self.clean],iter(self.bank))

def audit_example(config,model,metadata,row,directory):
 import numpy as np,torch
 from . import torch_ops as ops
 e=protocol.load_events(row);label=row['label'];a=config['attack'];radius=float(a['epsilon_fraction'])*(e.t[-1]-e.t[0]+1)
 d=Path(directory);d.mkdir(parents=True,exist_ok=True);cost=ops.costs();ops.sync(config.get('device','cpu'))
 started_verify=time.perf_counter()
 clean_logits=ops.evaluate(model,e,[e.t],label,cost,chunk=1,verification=True)[0]
 if core.prediction(clean_logits)!=label:raise ValueError('Frozen manifest contains clean-incorrect example; cell must not silently drop it')
 clean_cost=time.perf_counter()-started_verify;clean_candidate=core.Candidate(-1,e,clean_logits)
 raw_path=d/'candidate_times.f64'
 kwargs=dict(seed=int(a['seed']),trajectory_path=raw_path)
 if a['name']=='PGD':bank,search=ops.pgd(model,e,label,radius,steps=int(a['steps']),step_fraction=float(a['step_fraction']),restarts=int(a['restarts']),objective=a['objective'],**kwargs)
 elif a['name']=='TEMP':bank,search=ops.temp(model,e,label,radius,requested_q=int(a['requested_Q']),chunk=int(a.get('chunk',64)),**kwargs)
 else:raise ValueError('Unknown attack')
 objective=a['objective']
 original_logits=list(bank.values);ops.sync(config.get('device','cpu'));verify_start=time.perf_counter()
 verified=[];chunk=int(config.get('verification_chunk',1))
 for start in range(0,len(bank),chunk):
  times=[bank[i].events.t for i in range(start,min(start+chunk,len(bank)))]
  verified.extend(ops.evaluate(model,e,times,label,search,chunk=chunk,verification=True))
 # GPU/batch differences must be diagnosed, not silently turned into successes.
 tolerance=float(config.get('logit_tolerance',1e-5))
 discrepancy=max(abs(x-y) for u,v in zip(original_logits,verified) for x,y in zip(u,v))
 if any(core.prediction(a)!=core.prediction(b) for a,b in zip(original_logits,verified)):raise ValueError('Search/audit argmax changed; diagnose near-tie numerical differences')
 if discrepancy>tolerance:raise ValueError(f'Unexpected search/audit logit difference {discrepancy}; rerun with verified precision/chunk')
 bank.values=verified;common_selection=selection_audit(e,WithLogits(bank,original_logits),bank,label,radius,objective)
 selected=core.select(e,WithFallback(bank,clean_candidate),label,radius,objective)
 legacy_index=common_selection['legacy_output'];legacy_success=core.prediction(bank[legacy_index].logits)!=label
 selected_index=selected['success_priority_output'];chosen=clean_candidate if selected_index==-1 else bank[selected_index]
 selected['legacy_output']=legacy_index;selected['legacy_success']=legacy_success
 meta_rows=[]
 for i,c in enumerate(bank):
  check=core.validity(e,c.events,radius)
  meta_rows.append({'candidate_index':i,'loss':core.loss(c.logits,label,objective),'search_loss':core.loss(original_logits[i],label,objective),
   'prediction':core.prediction(c.logits),'search_prediction':core.prediction(original_logits[i]),'logits':list(c.logits),
   'validity':check,'success':check['valid'] and core.prediction(c.logits)!=label,
   'cumulative_evaluated_candidates':i+1,'raw_timestamp_ref':'candidate_times.f64' if str(row['example_id']) in config.get('full_trace_ids',[]) or not legacy_success and selected['any_valid_success'] else None})
 write_jsonl(d/'candidates.jsonl',meta_rows)
 arrays={k:np.asarray(getattr(e,k)) for k in ['ids','x','y','p','t']}
 arrays.update(attacked_t=np.asarray(chosen.events.t),clean_logits=np.asarray(clean_logits),attacked_logits=np.asarray(chosen.logits),label=np.asarray(label))
 diagnostics=None;state_ref=None;analysis_calls=0
 device=next(model.parameters()).device
 clean_state=ops.state_output(model,ops.frames(e,torch.tensor(e.t,device=device,dtype=torch.float32)))
 if clean_state is not None:
  attacked_state=ops.state_output(model,ops.frames(e,torch.tensor(chosen.events.t,device=device,dtype=torch.float32)))
  analysis_calls=2;cs,cq=clean_state;ads,aq=attacked_state
  diagnostics=core.state_metrics(cs.tolist(),ads.tolist(),cq.tolist(),aq.tolist(),tolerance=float(config.get('state_tolerance',2e-5)))
  bound=core.margin_bound(cq.tolist(),aq.tolist(),model.head.weight.detach().cpu().tolist(),model.head.bias.detach().cpu().tolist(),label,diagnostics['trace_distance'])
  if not bound['all_bounds_hold']:raise ValueError('State-margin lower bound failed numerical audit')
  diagnostics['readout_bound']=bound
  arrays.update(clean_state=cs.numpy(),attacked_state=ads.numpy(),clean_probabilities=cq.numpy(),attacked_probabilities=aq.numpy())
  state_ref=str(d/'selected_arrays.npz')
 np.savez_compressed(d/'selected_arrays.npz',**arrays)
 ops.sync(device);verification_elapsed=clean_cost+time.perf_counter()-verify_start
 search['verification_forward_calls']+=cost['verification_forward_calls'];search['verification_forward_equivalents']+=cost['verification_forward_equivalents']
 search.update(elapsed_verification_seconds=verification_elapsed,analysis_forward_calls=analysis_calls,
  verification_includes_validity_selection_state_analysis_and_serialization=True,verification_chunk=chunk,
  max_search_audit_logit_difference=discrepancy,unique_candidates=selected['unique_candidates'],examples_per_batch=1,
  device=str(device),peak_memory_bytes=torch.cuda.max_memory_allocated(device) if device.type=='cuda' else None,
  process_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
 keep_raw=str(row['example_id']) in config.get('full_trace_ids',[]) or not legacy_success and selected['any_valid_success']
 if keep_raw and isinstance(bank.times,np.memmap):bank.times.flush()
 if not keep_raw:raw_path.unlink()
 delta=np.abs(np.asarray(chosen.events.t)-np.asarray(e.t))
 clean_bins=np.floor((np.asarray(e.t,dtype=np.float32)-np.float32(e.t[0]))*np.float32(10)/np.float32(e.t[-1]-float(np.float32(e.t[0]))+1)).clip(0,9)
 adv_bins=np.floor((np.asarray(chosen.events.t,dtype=np.float32)-np.float32(e.t[0]))*np.float32(10)/np.float32(e.t[-1]-float(np.float32(e.t[0]))+1)).clip(0,9)
 artifacts={str(p):core.file_hash(p) for p in d.iterdir() if p.is_file()}
 return {'example_id':row['example_id'],'true_label':label,'status':'completed','clean_correct':True,
  'dataset_split':row['dataset_split'],'model_id':metadata['model_id'],'training_seed':metadata['training_seed'],'frontend_seed':metadata['frontend_seed'],
  'attack_seed':a['seed'],'attack_name':a['name'],'objective':objective,'selection_rule':'success_priority_v1',
  'budget_type':'duration_fraction','budget_value':a['epsilon_fraction'],'clean_pred':core.prediction(clean_logits),
  'attacked_pred':core.prediction(chosen.logits),'clean_logits':list(clean_logits),'attacked_logits':list(chosen.logits),
  'clean_margin':-core.loss(clean_logits,label,'margin'),'attacked_margin':-core.loss(chosen.logits,label,'margin'),
  'validity_pass':core.validity(e,chosen.events,radius)['valid'],'success':selected['any_valid_success'],
  'any_valid_success':selected['any_valid_success'],'legacy_success':legacy_success,'legacy_output':legacy_index,'search_legacy_output':common_selection['search_legacy_output'],'reevaluation_changed_selection':common_selection['reevaluation_changed_selection'],
  'success_priority_output':selected_index,'legacy_missed_success':not legacy_success and selected['any_valid_success'],
  'first_success_candidate':selected['first_success_candidate'],'best_so_far':selected['best_so_far'][1:],
  'event_count':len(e.t),'realized_linf_time':float(delta.max()),'realized_l1_time':float(delta.sum()),
  'num_shifted_events':int(np.count_nonzero(delta)),'hard_bin_changes':int(np.count_nonzero(clean_bins!=adv_bins)),
  'candidate_count':search['evaluated_candidates'],'forward_count':search['search_forward_equivalents'],
  'backward_count':search['backward_calls'],'verification_forward_calls':search['verification_forward_calls'],
  'search_seconds':search['elapsed_search_seconds'],'verification_seconds':search['elapsed_verification_seconds'],
  'cost':search,'state_diagnostics':diagnostics,'clean_state_ref':state_ref,'attacked_state_ref':state_ref,
  'state_capture_point':'after common learned measurement-basis unitary' if state_ref else None,
  'full_raw_candidate_trace_retained':keep_raw,'artifacts':artifacts,'evidence_status':'new_experiment'}

def attack(config,outdir=None):
 out=Path(outdir) if outdir else protocol.run_directory(config['run_id']);out.mkdir(parents=True,exist_ok=True)
 protocol.validate_attack_config(config)
 pre=protocol.preflight(config)
 identity_path=out/'run_identity.json'
 if pre['status']!='ready':
  if identity_path.exists():raise ValueError('Existing measured run now lacks prerequisites; its artifacts will not be overwritten')
  core.atomic_json(out/'preflight.json',pre);core.atomic_json(out/'config.json',config);core.atomic_json(out/'aggregates.json',pre);return pre
 configure(config);env=environment();identity=protocol.bind_run(out,config,env)
 core.atomic_json(out/'preflight.json',pre)
 if not (out/'config.json').exists():core.atomic_json(out/'config.json',config)
 if not (out/'environment.json').exists():core.atomic_json(out/'environment.json',env)
 manifest=inputs(config)
 if config['data'].get('expected_n') is not None and len(manifest)!=config['data']['expected_n']:raise ValueError('Manifest size differs from frozen config; no silent reduction')
 model,metadata=protocol.load_model(config)
 cfgsha=protocol.digest(config);srcsha=protocol.source_fingerprint();records=[]
 checkpoint_sha=config['model']['checkpoint_sha256']
 for row in manifest:
  stem=hashlib.sha256(str(row['example_id']).encode()).hexdigest();receipt=out/'records'/f'{stem}.json'
  if receipt.is_file():
   saved=json.loads(receipt.read_text())
   if protocol.can_resume(saved,cfgsha,srcsha,row['events_sha256'],checkpoint_sha):records.append(saved);continue
  try:record=audit_example(config,model,metadata,row,out/'trajectories'/stem)
  except Exception as exc:record={'example_id':row['example_id'],'status':'failed','clean_correct':None,'any_valid_success':None,'error':f'{type(exc).__name__}: {exc}','evidence_status':None}
  record.update(environment_fingerprint=identity['environment_fingerprint'],environment_ref=str(out/'environment.json'),run_id=config['run_id'],source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_fingerprint=srcsha,
   config_sha256=cfgsha,input_sha256=row['events_sha256'],checkpoint_sha256=checkpoint_sha)
  core.atomic_json(receipt,record);records.append(record)
 write_jsonl(out/'per_example.jsonl',records);write_jsonl(out/'timings.jsonl',[{'example_id':r['example_id'],'cost':r.get('cost')} for r in records])
 summary=core.aggregate(records,[r['example_id'] for r in manifest]);core.atomic_json(out/'aggregates.json',summary)
 complete=summary['status']=='completed'
 core.atomic_json(out/'selection_audit.json',{'status':'completed' if complete else 'incomplete','n':len(records) if complete else None,
  'legacy_missed_successes':sum(r.get('legacy_missed_success',False) for r in records) if complete else None,
  'example_ids':[r['example_id'] for r in records if r.get('legacy_missed_success')],
  'asr_delta':sum(r.get('legacy_missed_success',False) for r in records)/len(records) if complete else None,'same_candidate_trajectories':True})
 return summary

def pilot(config,outdir=None):
 out=Path(outdir) if outdir else ROOT/'Reports/phase3';out.mkdir(parents=True,exist_ok=True)
 pre=protocol.preflight(config);core.atomic_json(out/'pilot.json',pre);core.atomic_json(out/'environment.json',environment())
 if pre['status']!='ready':return pre
 manifest=inputs(config)
 if len(manifest)<1:raise ValueError('Pilot needs a real manifest')
 # A configured pilot manifest must be prepared separately; no hidden reduction of a campaign.
 if len(manifest)!=config['data']['expected_n']:raise ValueError('Pilot manifest length mismatch')
 result=attack(config,out/'measured-pilot')
 pre.update(status='smoke_passed' if result['status']=='completed' else 'failed',real_checkpoint_loaded=True,real_data_loaded=True,
  experimental_result_count=result['completed_count'],pilot_run_ref=str(out/'measured-pilot'),asr=result['asr'],estimated_campaign_seconds=None)
 core.atomic_json(out/'pilot.json',pre);return pre

def clean_eval(config,outdir=None):
 out=Path(outdir) if outdir else protocol.run_directory(config['run_id']);out.mkdir(parents=True,exist_ok=True)
 pre=protocol.preflight(config);core.atomic_json(out/'preflight.json',pre)
 if pre['status']!='ready':return pre
 configure(config);env=environment();identity=protocol.bind_run(out,config,env)
 if not (out/'config.json').exists():core.atomic_json(out/'config.json',config)
 if not (out/'environment.json').exists():core.atomic_json(out/'environment.json',env)
 manifest=inputs(config);protocol.require_complete_clean_test(manifest,config['stage'])
 model,metadata=protocol.load_model(config)
 from . import torch_ops as ops
 cost=ops.costs();rows=[];confusion=[[0]*10 for _ in range(10)];started=time.perf_counter()
 for row in manifest:
  e=protocol.load_events(row);z=ops.evaluate(model,e,[e.t],row['label'],cost,verification=True)[0];pred=core.prediction(z)
  confusion[row['label']][pred]+=1
  rows.append({**row,'model_id':metadata['model_id'],'prediction':pred,'clean_correct':pred==row['label'],'logits':list(z)})
 write_jsonl(out/'clean_predictions.jsonl',rows)
 fs=[]
 for k in range(10):
  tp=confusion[k][k];den=sum(confusion[k])+sum(x[k] for x in confusion)
  fs.append(2*tp/den if den else 0.)
 result={'status':'completed','n':len(rows),'correct':sum(r['clean_correct'] for r in rows),'accuracy':sum(r['clean_correct'] for r in rows)/len(rows),
  'macro_f1':sum(fs)/10,'class_counts':[sum(row) for row in confusion],'confusion':confusion,'elapsed_seconds':time.perf_counter()-started,
  'dataset_split':manifest[0]['dataset_split'],'evidence_status':'new_experiment','config_sha256':protocol.digest(config),'source_fingerprint':protocol.source_fingerprint(),
  'checkpoint_sha256':config['model']['checkpoint_sha256'],'manifest_sha256':config['data']['manifest_sha256'],
  'model_id':metadata['model_id'],'training_seed':metadata['training_seed'],'frontend_seed':metadata['frontend_seed'],
  'environment_fingerprint':identity['environment_fingerprint'],'environment_ref':str(out/'environment.json'),
  'clean_predictions_sha256':core.file_hash(out/'clean_predictions.jsonl')}
 core.atomic_json(out/'clean_metrics.json',result);return result

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['inventory','pilot','attack','clean-eval']);parser.add_argument('--config');args=parser.parse_args()
 if args.command=='inventory':result=inventory();print(json.dumps({'entries':len(result['artifacts']),'candidate_files':result['local_candidate_artifact_files']}));return
 if not args.config:parser.error('--config is required')
 cfg=protocol.load_config(args.config)
 result={'pilot':pilot,'attack':attack,'clean-eval':clean_eval}[args.command](cfg)
 print(json.dumps(result,indent=2));raise SystemExit(2 if result['status'] in ['blocked_resource','incomplete','failed'] else 0)


def selection_audit(clean,search,verified,label,radius,objective):
 search_choice=core.select(clean,search,label,radius,objective)
 common=core.select(clean,verified,label,radius,objective)
 common.update(search_legacy_output=search_choice['legacy_output'],
  legacy_missed_success=not common['legacy_success'] and common['any_valid_success'],
  reevaluation_changed_selection=common['legacy_output']!=search_choice['legacy_output'])
 return common

if __name__=='__main__':main()
