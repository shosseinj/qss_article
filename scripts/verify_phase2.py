"""Lightweight manuscript/data checks. Does not import or execute model runners."""
from pathlib import Path
import ast,csv,hashlib,json,math,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
def read_csv(path):
 with (ROOT/path).open(newline='') as f:return list(csv.DictReader(f))

def check_document(name):
 def expand(path):
  s=(ROOT/path).read_text()
  return re.sub(r'\\input\{([^}]+)\}',lambda m:expand(m[1]+'.tex'),s)
 tex=expand(name+'.tex')
 labels=re.findall(r'\\label\{([^}]+)\}',tex)
 assert len(labels)==len(set(labels)),('duplicate labels',name)
 refs=re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',tex)
 assert set(refs)<=set(labels),(name,'missing reference',set(refs)-set(labels))
 bib=(ROOT/'references.bib').read_text()
 keys=re.findall(r'@\w+\{([^,]+)',bib)
 assert len(keys)==len(set(keys))==20
 cites={k for group in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}',tex) for k in group.split(',')}
 assert cites<=set(keys),(name,cites-set(keys))
 log=(ROOT/'build'/f'{name}.log').read_text()
 assert not re.search(r'undefined|multiply defined|Overfull|LaTeX Warning',log),name
 assert 'Output written on' in log,name
 return {'labels':len(labels),'citations':len(cites),'pdf_sha256':hashlib.sha256((ROOT/'build'/f'{name}.pdf').read_bytes()).hexdigest()}

paired=read_csv('data/timestamp_paired.csv')
for row in paired:
 b,c,both,neither=(int(row[k]) for k in ['pgd_only','temp_only','both','neither'])
 assert b+c+both+neither==100
 assert math.isclose(float(row['pgd_asr_fraction']),(both+b)/100)
 assert math.isclose(float(row['temp_asr_fraction']),(both+c)/100)
 discord=b+c
 p=min(1,2*sum(math.comb(discord,i) for i in range(min(b,c)+1))/2**discord) if discord else 1
 assert math.isclose(p,float(row['recomputed_exact_p']))
# Inspect literal definitions only, without loading scientific model dependencies.
source=ROOT/'data/evidence_source_snapshot/scripts/run_nmnist_budget_matched_comparison_v2_seed42.py'
tree=ast.parse(source.read_text())
condition_node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONDITIONS' for t in n.targets))
conditions=ast.literal_eval(condition_node.value)
for name,d in conditions.items():
 assert d['initial']>=12 and d['generations']==4
 assert d['initial']+4*d['per_generation']==d['q']==(21 if '21' in name else 41)
for q in [1600,4000]:
 n0=max(12,round(.375*q));ng=round((q-n0)/4)
 assert n0+4*ng==q
# Verify derived Wilson exports independently from the plotting script.
for row in read_csv('Reports/phase2-wilson-intervals.csv'):
 n=int(row['n']);s=int(row['successes']);z=1.959963984540054;p=s/n;den=1+z*z/n
 cen=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 assert abs(float(row['wilson95_low_percent'])-100*(cen-half))<1e-10
 assert abs(float(row['wilson95_high_percent'])-100*(cen+half))<1e-10
 original=next(x for x in paired if x['condition']==row['condition'] and x['model']==row['model'] and x['epsilon_fraction']==row['epsilon_fraction'])
 assert s==int(original['both'])+int(original['pgd_only' if row['method']=='PGD' else 'temp_only'])
# The scientific evidence files must have zero changes against the current Git baseline.
assert not subprocess.check_output(['git','diff','--name-only','--','data/'],cwd=ROOT,text=True).strip()
# Vector scientific figures must not contain embedded raster images.
for i,name in enumerate(['fig01_overview','fig02_matched_evaluation','fig03_grid_comparison'],1):
 listing=subprocess.check_output(['pdfimages','-list',str(ROOT/'figures'/f'{name}.pdf')],text=True)
 assert len(listing.strip().splitlines())==2,(name,listing)
 for ext in ['pdf','svg','png']: assert (ROOT/'figures'/f'{name}.{ext}').stat().st_size>0
report={'status':'passed','documents':{d:check_document(d) for d in ['main','supplement']},
 'bibliography_keys':20,'paired_rows_verified':len(paired),'low_Q_schedules_verified':conditions,
 'source_data_unchanged':True,'scientific_figures_vector':True,
 'checks':'counts, exact McNemar p-values, Wilson exports, citation/reference resolution, unique keys/labels, build logs and source data diff',
 'not_performed':'training, attack reruns, original raw-data audit or recovery of missing run artifacts'}
(ROOT/'Reports/phase2-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
