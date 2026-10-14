"""Render phase2 results from preserved CSV counts; no model execution.

Requires Python 3 and Matplotlib (NumPy is a Matplotlib dependency).
Run: MPLCONFIGDIR=/tmp/qsnn-mpl python3 scripts/render_phase2_figures.py
Method diagram source: figures/fig01_overview.tex (TikZ).
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT=Path(__file__).resolve().parents[1]
INK='#17324B'; TEAL='#007C83'; ORANGE='#C56E1A'; GREY='#E5EBEF'; MAGENTA='#AA3377'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':8,
 'axes.titlesize':9,'xtick.labelsize':7.5,'ytick.labelsize':8,'text.color':INK,
 'axes.labelcolor':INK,'axes.edgecolor':'#9AA9B5','xtick.color':INK,'ytick.color':INK,
 'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','savefig.dpi':300})

def rows(path):
 with (ROOT/path).open(newline='') as f:return list(csv.DictReader(f))

def wilson(s,n):
 z=1.959963984540054;p=s/n;d=1+z*z/n
 c=(p+z*z/(2*n))/d
 h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return max(0,c-h)*100,min(1,c+h)*100

def save(fig,name):
 for ext in ['pdf','svg','png']:
  path=ROOT/'figures'/f'{name}.{ext}'
  fig.savefig(path,facecolor='white')
  if ext=='svg': path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
 plt.close(fig)

def style(ax):
 for side in ['top','right']:ax.spines[side].set_visible(False)
 ax.set_axisbelow(True)
 ax.grid(axis='x',color='#E3E9EE',lw=.65)

paired=rows('data/timestamp_paired.csv')
qs=[x for x in paired if x['model']=='QSNN' and x['condition'] in ['access_candidates_21','wallclock_qsnn']]
assert len(qs)==4
# Explicitly validate why forward matching can share an aggregate display.
for a in [x for x in paired if x['condition']=='access_candidates_21']:
 b=next(x for x in paired if x['condition']=='access_forwards_41' and x['model']==a['model'] and x['epsilon_fraction']==a['epsilon_fraction'])
 for key in ['pgd_only','temp_only','both','neither']:
  assert a[key]==b[key],(a,b,key)
intervals=[]
fig,(ax,overlap)=plt.subplots(1,2,figsize=(7.25,3.1),gridspec_kw={'width_ratios':[1.1,1.22]})
fig.subplots_adjust(left=.18,right=.98,bottom=.20,top=.80,wspace=.27)
ypos=[3,2,1,0]
labels=['Access: 5%','Access: 10%','Time: 5%','Time: 10%']
for row,y in zip(qs,ypos):
 both,b,c,neither=(int(row[k]) for k in ['both','pgd_only','temp_only','neither'])
 assert both+b+c+neither==100
 assert math.isclose(float(row['pgd_asr_fraction']), (both+b)/100)
 assert math.isclose(float(row['temp_asr_fraction']), (both+c)/100)
 for method,count,color,marker,offset in [('PGD',both+b,INK,'o',.11),('TEMP',both+c,MAGENTA,'s',-.11)]:
  lo,hi=wilson(count,100)
  ax.errorbar(count,y+offset,xerr=[[count-lo],[hi-count]],fmt=marker,color=color,ms=4,capsize=2,lw=1)
  ax.text(count+.25,y+offset+.055,str(count),fontsize=7,color=color)
  intervals.append({'condition':row['condition'],'model':'QSNN','epsilon_fraction':row['epsilon_fraction'],
   'method':method,'successes':count,'n':100,'ASR_percent':count,'wilson95_low_percent':lo,'wilson95_high_percent':hi})
ax.set(yticks=ypos,yticklabels=labels,xlim=(0,12.5),ylim=(-.55,3.55),xlabel='ASR (%) · 95% Wilson score interval')
ax.set_title('a  Success rates',loc='left',fontweight='bold',pad=22)
style(ax)
ax.legend(handles=[Line2D([],[],color=INK,marker='o',label='PGD',lw=1),Line2D([],[],color=MAGENTA,marker='s',label='TEMP',lw=1)],loc='upper left',bbox_to_anchor=(0,1.12),ncol=2,frameon=False,fontsize=7)
# Each of four overlap categories is explicit; zero PGD-only counts are visible.
colors=[INK,ORANGE,MAGENTA,GREY]; hatches=['','//','xx','']
for row,y in zip(qs,ypos):
 vals=[int(row[k]) for k in ['both','pgd_only','temp_only','neither']]
 left=0
 for value,color,hatch in zip(vals,colors,hatches):
  overlap.barh(y,value,left=left,height=.58,color=color,hatch=hatch,edgecolor='white',lw=.4)
  left+=value
 overlap.text(101,y,' / '.join(str(v) for v in vals),va='center',fontsize=7)
overlap.set(yticks=ypos,yticklabels=[],xlim=(0,170),ylim=(-.55,3.55),xlabel='Examples (n=100)',xticks=[0,50,100])
overlap.text(101,3.55,'B / P / T / N',fontsize=6.7,ha='left',va='bottom')
overlap.set_title('b  Paired overlap',loc='left',fontweight='bold',pad=22)
style(overlap)
for side in ['left','right']: overlap.spines[side].set_visible(False)
overlap.tick_params(axis='y',length=0)
fig.legend(handles=[Patch(facecolor=c,hatch=h,edgecolor=INK if h else c,label=l) for c,h,l in zip(colors,hatches,['Both','PGD-only','TEMP-only','Neither'])],loc='lower center',bbox_to_anchor=(.55,.005),ncol=4,frameon=False,fontsize=7)
save(fig,'fig02_matched_evaluation')

# Two panels, full range with declared insets. No clean-accuracy encoding.
grid=rows('data/controlled_four_models.csv')
fig,axes=plt.subplots(1,2,figsize=(7.25,3.5),sharey=True)
fig.subplots_adjust(left=.20,right=.99,bottom=.18,top=.83,wspace=.18)
model_order=['custom','convnet','resnet18','vggsnn']
names=['Custom SNN','ConvNet','Spiking ResNet18','VGGSNN']
budgets=[('asr_Binf_1_percent',TEAL,'o',.10),('asr_B0_200_percent',ORANGE,'s',-.10)]
for ax,rep,title in zip(axes,['Binary','Integer'],['a  Binary packets','b  Integer packets']):
 rs=[next(x for x in grid if x['representation']==rep and x['model']==m) for m in model_order]
 for x in rs: assert int(x['attack_denominator'])==1000
 for i,row in enumerate(rs):
  y=3-i
  for key,color,marker,dy in budgets:
   value=float(row[key])
   ax.plot(value,y+dy,marker=marker,color=color,ms=4,linestyle='none')
   if i==0:ax.text(value-1.7,y+dy,f'{value:.1f}',ha='right',va='center',fontsize=7,color=color)
 ax.set(yticks=[3,2,1,0],yticklabels=names,xlim=(-2,103),ylim=(-.6,3.6),xticks=[0,25,50,75,100],xlabel='Attack success rate (%)')
 ax.set_title(title,loc='left',fontweight='bold',pad=9)
 style(ax)
 # Reserved empty high-ASR region houses a clearly labelled magnification.
 inset=ax.inset_axes([.36,.08,.60,.57])
 for i,row in enumerate(rs[1:]):
  y=2-i
  for key,color,marker,dy in budgets:
   v=float(row[key]);inset.plot(v,y+dy,marker=marker,color=color,ms=3.5,linestyle='none')
   inset.text(v-.07 if v>1.6 else v+.07,y+dy,f'{v:.1f}',ha='right' if v>1.6 else 'left',va='center',fontsize=6.7,color=color)
 inset.set(xlim=(-.08,2.1),ylim=(-.45,2.45),xticks=[0,1,2],yticks=[2,1,0],yticklabels=['Conv','Res18','VGG'])
 inset.set_title('Inset: controls, 0–2.1%',fontsize=7,pad=5)
 inset.tick_params(labelsize=6.5,length=2)
 inset.spines[['top','right']].set_visible(False)
 inset.grid(axis='x',color='#E3E9EE',lw=.5)
 inset.set_facecolor('#F8FAFC')
 # Keep the small-value inset on its explicitly stated 0–2.1% range.
 inset.set_xticks([0,1,2.1],labels=['0','1','2.1'])
fig.legend(handles=[Line2D([],[],color=TEAL,marker='o',linestyle='none',label=r'$B_\infty=1$ bin'),Line2D([],[],color=ORANGE,marker='s',linestyle='none',label=r'$B_0=200$ packets')],loc='upper center',ncol=2,frameon=False,bbox_to_anchor=(.56,1.00))
save(fig,'fig03_grid_comparison')
with (ROOT/'Reports/phase2-wilson-intervals.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(intervals[0]));w.writeheader();w.writerows(intervals)
meta={'source_commit':'80d02f5733d4cbe7c3e69b828dff66d50ba5c211',
 'script':'scripts/render_phase2_figures.py','matplotlib_version':matplotlib.__version__,
 'data':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['data/timestamp_paired.csv','data/controlled_four_models.csv']},
 'figure1':'TikZ source matches preserved model; schematic computation, no invented event example',
 'figure2':'QSNN n=100, seed42 validation; candidate/forward aggregates checked equal; 95% Wilson, not paired-difference or population intervals',
 'figure3':'n=1000 per cell, separate manifests; counts from controlled local report; no error bars or cross-representation pairing',
 'budget_palette':{'B_inf':TEAL,'B_0':ORANGE},'intervals':intervals}
(ROOT/'Reports/phase2-figure-provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
print('Rendered vector PDF/SVG and 300-dpi PNG figures 2/3; wrote counts/interval provenance.')
