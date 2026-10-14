"""Dependency-free scientific contracts for Phase 3 (no historical mutation)."""
from dataclasses import dataclass,replace
import hashlib,json,math,random
from pathlib import Path

@dataclass(frozen=True)
class Events:
 ids:tuple
 x:tuple
 y:tuple
 p:tuple
 t:tuple
 def with_times(self,t):return replace(self,t=tuple(float(v) for v in t))

@dataclass(frozen=True)
class Candidate:
 index:int
 events:Events
 logits:tuple

def validity(clean,adv,radius,tolerance=1e-8):
 if not math.isfinite(radius) or radius<0 or not math.isfinite(tolerance) or tolerance<0:raise ValueError('Invalid radius/tolerance')
 n=len(clean.t)
 if n==0 or any(len(getattr(clean,k))!=n for k in ['ids','x','y','p']):raise ValueError('Invalid clean event lengths')
 if len(set(clean.ids))!=n or not all(math.isfinite(t) for t in clean.t) or any(a>b for a,b in zip(clean.t,clean.t[1:])):raise ValueError('Invalid clean identity/timestamps')
 checks={k+'_ok':getattr(clean,k)==getattr(adv,k) for k in ['ids','x','y','p']}
 checks['count_ok']=all(len(getattr(adv,k))==n for k in ['ids','x','y','p','t'])
 finite=all(math.isfinite(t) for t in adv.t)
 checks['finite_ok']=finite
 checks['timestamp_bounds_ok']=bool(checks['count_ok'] and finite and all(clean.t[0]-tolerance<=t<=clean.t[-1]+tolerance and abs(t-c)<=radius+tolerance for t,c in zip(adv.t,clean.t)))
 checks['ordered_ok']=finite and all(a<=b+tolerance for a,b in zip(adv.t,adv.t[1:]))
 checks['valid']=all(checks.values());return checks

def feasible(proposal,clean_times,radius):
 if len(proposal)!=len(clean_times) or not clean_times or not all(math.isfinite(t) for t in proposal):raise ValueError('Malformed proposal')
 if radius<0 or not math.isfinite(radius):raise ValueError('Invalid radius')
 out=[];previous=-math.inf
 for value,c in zip(proposal,clean_times):
  value=max(c-radius,min(c+radius,float(value)));value=max(previous,value)
  value=max(clean_times[0],min(clean_times[-1],value));out.append(value);previous=value
 return tuple(out)

def prediction(logits):
 if len(logits)<2 or not all(math.isfinite(v) for v in logits):raise ValueError('Nonfinite/invalid logits')
 # torch.argmax-compatible: the first class index wins a tie.
 return max(range(len(logits)),key=lambda k:logits[k])

def loss(logits,label,objective):
 prediction(logits)
 if not 0<=label<len(logits):raise ValueError('Invalid label')
 if objective=='ce':
  top=max(logits);return top+math.log(sum(math.exp(v-top) for v in logits))-logits[label]
 if objective=='margin':return max(v for i,v in enumerate(logits) if i!=label)-logits[label]
 raise ValueError('Unknown objective')

def select(clean,candidates,label,radius,objective,tolerance=1e-8):
 if not candidates:raise ValueError('No evaluated candidates')
 if len({c.index for c in candidates})!=len(candidates):raise ValueError('Duplicate candidate index')
 legacy=None;priority=None;first=None;best=[];ever=False;valid_count=0;unique=set()
 rank=lambda c:(loss(c.logits,label,objective),-c.index)
 import struct
 for c in candidates:
  ok=validity(clean,c.events,radius,tolerance)['valid'];pred=prediction(c.logits)
  unique.add(hashlib.sha256(struct.pack(f"<{len(c.events.t)}d",*c.events.t)).digest())
  if ok:
   valid_count+=1
   if legacy is None or rank(c)>rank(legacy):legacy=c
   if pred!=label:
    if first is None:first=c.index
    ever=True
    if priority is None or rank(c)>rank(priority):priority=c
  best.append(ever)
 if legacy is None:raise ValueError('No valid fallback; failed run, not survivor')
 priority=priority or legacy
 return {'legacy_output':legacy.index,'legacy_success':prediction(legacy.logits)!=label,
  'any_valid_success':ever,'success_priority_output':priority.index,
  'first_success_candidate':first,'evaluated_candidates':len(candidates),'unique_candidates':len(unique),
  'valid_candidates':valid_count,'best_so_far':best}

def temp_schedule(requested_q):
 if not isinstance(requested_q,int) or requested_q<16:raise ValueError('Budget too small for 12 elites and four nonempty generations')
 if requested_q in [21,41]:initial,children=13,(2 if requested_q==21 else 7)
 else:initial=max(12,round(.375*requested_q));children=round((requested_q-initial)/4)
 if children<1:raise ValueError('Nonempty generations required')
 return initial,4,children,initial+4*children

def wilson(s,n):
 if n<=0 or not 0<=s<=n:raise ValueError('Invalid numerator/denominator')
 z=1.959963984540054;p=s/n;d=1+z*z/n
 c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [max(0,c-h),min(1,c+h)]

def paired_counts(pgd,temp):
 if set(pgd)!=set(temp):raise ValueError('Paired ID sets differ')
 b=sum(pgd[k] and not temp[k] for k in pgd);c=sum(temp[k] and not pgd[k] for k in pgd)
 d=b+c;p=min(1.,2*sum(math.comb(d,i) for i in range(min(b,c)+1))/2**d) if d else 1.
 return {'both':sum(pgd[k] and temp[k] for k in pgd),'pgd_only':b,'temp_only':c,
  'neither':sum(not pgd[k] and not temp[k] for k in pgd),'n':len(pgd),
  'temp_minus_pgd':(c-b)/len(pgd) if pgd else None,'exact_mcnemar_p':p}

def aggregate(records,manifest_ids):
 ids=list(manifest_ids)
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate manifest IDs')
 by={}
 for r in records:
  i=r['example_id']
  if i in by or i not in ids:raise ValueError('Duplicate or foreign example ID')
  by[i]=r
 incomplete=[i for i in ids if i not in by or by[i].get('status')!='completed' or by[i].get('clean_correct') is not True or not isinstance(by[i].get('any_valid_success'),bool)]
 done=[by[i] for i in ids if i not in incomplete]
 s=sum(x['any_valid_success'] for x in done)
 return {'status':'incomplete' if incomplete else 'completed','planned_denominator':len(ids),
  'completed_count':len(done),'observed_successes':s,'successes':None if incomplete else s,
  'missing_or_failed':incomplete,'asr':None if incomplete or not ids else s/len(ids),
  'wilson95':None if incomplete or not ids else wilson(s,len(ids))}

def stratified_manifest(rows,n,seed,classes=10):
 if n<1 or classes<1:raise ValueError('Invalid sample target')
 if len({r['example_id'] for r in rows})!=len(rows):raise ValueError('Duplicate pool IDs')
 pools={c:sorted([r for r in rows if r['label']==c],key=lambda r:str(r['example_id'])) for c in range(classes)}
 if sum(map(len,pools.values()))!=len(rows):raise ValueError('Invalid class label')
 rng=random.Random(seed)
 for values in pools.values():rng.shuffle(values)
 chosen=[]
 # Round-robin quota allocation, redistributing shortages deterministically.
 while len(chosen)<n:
  advanced=False
  for c in range(classes):
   if pools[c] and len(chosen)<n:chosen.append(pools[c].pop());advanced=True
  if not advanced:break
 return chosen

def state_metrics(clean,adv,q,qp,tolerance=1e-5):
 if len(clean)!=len(adv) or len(q)!=len(qp) or len(clean)!=len(q) or not clean:raise ValueError('State/probability shape mismatch')
 for state in [clean,adv]:
  if not all(math.isfinite(z.real) and math.isfinite(z.imag) for z in state) or abs(sum(abs(z)**2 for z in state)-1)>tolerance:raise ValueError('State is not normalized')
 for probs in [q,qp]:
  if any(not math.isfinite(v) or v<-tolerance for v in probs) or abs(sum(probs)-1)>tolerance:raise ValueError('Invalid probability vector')
 f=abs(sum(complex(a).conjugate()*b for a,b in zip(clean,adv)))**2
 if f>1+tolerance:raise ValueError('Fidelity error exceeds numerical tolerance')
 f=max(0.,min(1.,f));d=math.sqrt(max(0.,1-f));tv=.5*sum(abs(a-b) for a,b in zip(q,qp))
 if tv>d+tolerance:raise ValueError('Measurement contraction violated')
 return {'squared_fidelity':f,'trace_distance':d,'total_variation':tv,'normalization_tolerance':tolerance,'contraction_holds':True}

def margin_bound(q,qp,weights,bias,label,distance,tolerance=1e-5):
 if len(weights)!=len(bias) or len(weights)<2 or not 0<=label<len(weights) or len(q)!=len(qp) or any(len(w)!=len(q) for w in weights):raise ValueError('Readout shapes')
 if not math.isfinite(distance) or not 0<=distance<=1+tolerance:raise ValueError('Invalid trace distance')
 rows=[]
 for k in range(len(weights)):
  if k==label:continue
  diff=[a-b for a,b in zip(weights[label],weights[k])]
  clean=sum(a*b for a,b in zip(diff,q))+bias[label]-bias[k]
  actual=sum(a*b for a,b in zip(diff,qp))+bias[label]-bias[k]
  bound=clean-2*max(abs(v) for v in diff)*distance
  rows.append({'competitor':k,'clean_margin':clean,'attacked_margin':actual,'lower_bound':bound,'holds':actual+tolerance>=bound})
 return {'rows':rows,'all_bounds_hold':all(x['holds'] for x in rows),'sufficient_positive':all(x['lower_bound']>0 for x in rows)}

def file_hash(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def atomic_json(path,value):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 data=json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n'
 tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(data);tmp.replace(p)
