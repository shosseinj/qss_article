"""Versioned PyTorch search, explicit state export and hard/soft frame adapter.
Historical files are imported read-only from the hash-verified recovery directory.
No model is trained, downloaded or loaded implicitly.
"""
from pathlib import Path
import importlib,math,sys,time
import numpy as np
import torch
from torch import nn
from . import core
SOURCE=Path(__file__).resolve().parents[2]/'results/phase3/recovery/source'

def historical_models():
 if str(SOURCE) not in sys.path:sys.path.insert(0,str(SOURCE))
 module=importlib.import_module('models.nmnist_hybrid_qsnn')
 if Path(module.__file__).resolve()!=SOURCE/'models/nmnist_hybrid_qsnn.py':raise RuntimeError('Unexpected model module origin')
 return module

def frames(events,timestamps):
 if not core.validity(events,events,0)['valid']:raise ValueError('Invalid clean events')
 if any(not 0<=x<34 for x in events.x) or any(not 0<=y<34 for y in events.y) or any(p not in [0,1] for p in events.p):raise ValueError('Coordinates/polarity outside sensor')
 if timestamps.ndim==1:timestamps=timestamps[None,:]
 if timestamps.shape[1]!=len(events.t):raise ValueError('Timestamp length mismatch')
 device,dtype=timestamps.device,timestamps.dtype
 t0=torch.tensor(np.float32(events.t[0]),device=device,dtype=dtype)
 duration=torch.tensor(np.float32(max(events.t[-1]-float(np.float32(events.t[0]))+1.,1.)),device=device,dtype=dtype)
 u=(timestamps-t0)*torch.tensor(np.float32(10),device=device,dtype=dtype)/duration
 hard_bin=u.floor().long().clamp(0,9)
 centers=torch.arange(10,device=device,dtype=dtype)+.5
 weights=(1-(u[...,None]-centers).abs()).clamp_min(0)
 channel=torch.as_tensor(np.asarray(events.p)*1156+np.asarray(events.y)*34+np.asarray(events.x),device=device,dtype=torch.long)[None,:].expand(len(timestamps),-1)
 hard=torch.zeros((len(timestamps),10*2312),device=device,dtype=dtype)
 hard.scatter_add_(1,hard_bin*2312+channel,torch.ones_like(timestamps))
 soft=torch.zeros_like(hard)
 for b in range(10):soft.scatter_add_(1,torch.full_like(channel,b)*2312+channel,weights[:,:,b])
 return (soft+(hard-soft).detach()).reshape(-1,10,2,34,34).clamp_max(255)

def build_model(variant='qsnn',freeze_frontend=False):
 hist=historical_models()
 class StateHead(hist.QuantumHeadV2):
  def __init__(self,no_entanglers=False):
   super().__init__(n_blocks=2,learned_projection=True,two_axis_encoding=True,learned_measurement=True,topology='ring')
   self.no_entanglers=no_entanglers
  def _entangle(self,state,block):return state if self.no_entanglers else super()._entangle(state,block)
  def forward_state(self,latent):
   angles=math.pi*self.angle_projection(latent).clamp(-1.,1.)
   state=torch.zeros((len(latent),256),dtype=torch.complex64,device=latent.device);state[:,0]=1
   for block in range(2):
    for wire in range(8):
     state=self._ry(state,angles[:,wire],wire)
     state=self._rz(state,self.phase_scale[block,wire]*angles[:,wire],wire)
     state=self._ry(state,self.weights[block,wire,0].expand(len(latent)),wire)
     state=self._rz(state,self.weights[block,wire,1].expand(len(latent)),wire)
    state=self._entangle(state,block)
   for wire in range(8):
    state=self._rz(state,self.measurement_angles[wire,0].expand(len(latent)),wire)
    state=self._ry(state,self.measurement_angles[wire,1].expand(len(latent)),wire)
   return state
  def forward(self,latent):return self.forward_state(latent).abs().square()
 extractor=hist.NMNISTSpatialLIFExtractor(channels=(16,32),spatial_size=4,latent_dim=32,decay=.5)
 if variant in ['qsnn','qsnn_no_entanglers']:
  model=hist.NMNISTHybridQSNNV2(extractor=extractor,latent_dim=32,n_blocks=2,learned_projection=True,two_axis_encoding=True,learned_measurement=True,topology='ring')
  # Preserve initialization/key layout, extending only the state-access API.
  head=StateHead(variant=='qsnn_no_entanglers');head.load_state_dict(model.quantum.state_dict());model.quantum=head
 elif variant=='classical_head':
  class Classical(nn.Module):
   def __init__(self):
    super().__init__();self.extractor=extractor;self.head=nn.Sequential(nn.Linear(32,69),nn.Tanh(),nn.Linear(69,10))
   def forward(self,x):return self.head(self.extractor(x))
  model=Classical()
 elif variant=='snn':
  model=importlib.import_module('models.nmnist_snn').NMNISTConvSNN(.5,10)
 else:raise ValueError('Unknown variant')
 if freeze_frontend:
  for p in model.extractor.parameters():p.requires_grad_(False)
 return model

class CandidateBank:
 """Disk-backed timestamps keep Q*N arrays out of Python-object RAM."""
 def __init__(self,events,capacity,path=None):
  self.clean=events;self.values=[];self.n=0
  self.path=Path(path) if path else None
  if self.path:
   self.path.parent.mkdir(parents=True,exist_ok=True)
   self.times=np.memmap(self.path,dtype='float64',mode='w+',shape=(capacity,len(events.t)))
  else:self.times=[]
 def append(self,times,logits):
  if self.path:self.times[self.n]=times
  else:self.times.append(np.asarray(times,dtype=np.float64).copy())
  self.values.append(tuple(float(x) for x in logits));self.n+=1
 def __len__(self):return self.n
 def __getitem__(self,i):
  if not 0<=i<self.n:raise IndexError(i)
  return core.Candidate(i,self.clean.with_times(self.times[i]),self.values[i])
 def __iter__(self):
  for i in range(self.n):yield self[i]

def sync(device):
 if torch.device(device).type=='cuda':torch.cuda.synchronize(device)

def costs(requested=None):
 return {'requested_Q':requested,'actual_Q':0,'evaluated_candidates':0,'search_forward_calls':0,
 'search_forward_equivalents':0,'backward_calls':0,'verification_forward_calls':0,
 'verification_forward_equivalents':0,'elapsed_search_seconds':None,'elapsed_verification_seconds':None,
 'forward_unit':'calls are batched API invocations; equivalents count individual candidate examples',
 'dtype':'float32 / complex64 circuit','search_variant':'phase3_v1_no_forward_reuse'}

def evaluate(model,events,times,label,counters,chunk=64,verification=False):
 if chunk<1:raise ValueError('Invalid chunk')
 device=next(model.parameters()).device
 result=[]
 for start in range(0,len(times),chunk):
  part=times[start:start+chunk]
  tensor=torch.as_tensor(np.asarray(part),device=device,dtype=torch.float32)
  with torch.no_grad():logits=model(frames(events,tensor)).detach().cpu().tolist()
  prefix='verification' if verification else 'search'
  counters[prefix+'_forward_calls']+=1;counters[prefix+'_forward_equivalents']+=len(part)
  if not verification:counters['evaluated_candidates']+=len(part)
  result.extend(tuple(float(v) for v in row) for row in logits)
 return result

def pgd(model,events,label,radius,steps=20,step_fraction=.2,seed=42,restarts=1,objective='ce',trajectory_path=None):
 if steps<1 or restarts<1 or step_fraction<=0:raise ValueError('Invalid PGD config')
 model.eval();device=next(model.parameters()).device;counter=costs((steps+1)*restarts)
 bank=CandidateBank(events,(steps+1)*restarts,trajectory_path);rng=np.random.default_rng(seed);gradient_stats=[]
 sync(device);started=time.perf_counter()
 for restart in range(restarts):
  raw=events.t if restart==0 else core.feasible(np.asarray(events.t)+rng.uniform(-radius,radius,len(events.t)),events.t,radius)
  x=torch.tensor(raw,device=device,dtype=torch.float32)
  for step in range(steps+1):
   logits=evaluate(model,events,[x.detach().cpu().numpy()],label,counter,chunk=1)[0]
   bank.append(core.feasible(x.detach().cpu().numpy(),events.t,radius),logits)
   if step==steps:break
   x=x.detach().requires_grad_(True);z=model(frames(events,x))
   counter['search_forward_calls']+=1;counter['search_forward_equivalents']+=1
   if objective=='ce':loss=torch.nn.functional.cross_entropy(z,torch.tensor([label],device=device))
   elif objective=='margin':
    competitor=z.clone();competitor[:,label]=-torch.inf;loss=competitor.max(1).values[0]-z[0,label]
   else:raise ValueError('Unknown PGD objective')
   grad,=torch.autograd.grad(loss,x);counter['backward_calls']+=1
   if not torch.isfinite(grad).all():raise RuntimeError('Nonfinite timestamp gradient')
   gradient_stats.append({'restart':restart,'step':step,'zero_fraction':float((grad==0).float().mean()),'max_abs':float(grad.abs().max())})
   raw=core.feasible((x.detach()+radius*step_fraction*grad.sign()).cpu().numpy(),events.t,radius)
   x=torch.tensor(raw,device=device,dtype=torch.float32)
 sync(device);counter['elapsed_search_seconds']=time.perf_counter()-started
 counter['actual_Q']=len(bank);counter['candidate_chunk']=1;counter['gradient_statistics']=gradient_stats
 return bank,counter

def temp(model,events,label,radius,requested_q=21,seed=42,chunk=64,trajectory_path=None):
 model.eval();device=next(model.parameters()).device;n0,generations,ng,actual=core.temp_schedule(requested_q)
 counter=costs(requested_q);bank=CandidateBank(events,actual,trajectory_path);rng=np.random.default_rng(seed)
 sync(device);started=time.perf_counter()
 pool=np.asarray([core.feasible(np.asarray(events.t)+rng.uniform(-radius,radius,len(events.t)),events.t,radius) for _ in range(n0)])
 logits=evaluate(model,events,pool,label,counter,chunk)
 for t,z in zip(pool,logits):bank.append(t,z)
 scores=np.array([core.loss(z,label,'margin') for z in logits])
 # loss() is the negated true-class margin: higher is better.
 for scale in [.50,.30,.18,.10]:
  elite_idx=np.argsort(-scores,kind='stable')[:12];elite=pool[elite_idx];children=[]
  for i in range(ng):
   proposal=elite[i%12]+.5*(elite[rng.integers(12)]-elite[rng.integers(12)])+rng.normal(0,radius*scale,len(events.t))
   children.append(core.feasible(proposal,events.t,radius))
  children=np.asarray(children);child_z=evaluate(model,events,children,label,counter,chunk)
  for t,z in zip(children,child_z):bank.append(t,z)
  pool=np.vstack([elite,children]);scores=np.concatenate([scores[elite_idx],[core.loss(z,label,'margin') for z in child_z]])
 sync(device);counter['elapsed_search_seconds']=time.perf_counter()-started
 counter.update(actual_Q=len(bank),candidate_chunk=chunk,initial=n0,generations=generations,children_per_generation=ng)
 return bank,counter

@torch.no_grad()
def state_output(model,frame):
 if not hasattr(model,'quantum'):return None
 latent=torch.tanh(model.quantum_projection(model.extractor(frame)))
 state=model.quantum.forward_state(latent.float());q=state.abs().square()
 return state[0].cpu(),q[0].cpu()
