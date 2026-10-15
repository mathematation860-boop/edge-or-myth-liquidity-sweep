from bt import run
import pandas as pd, sys
def q(df):
    if not len(df): return 'none'
    df=df.copy(); df['q']=df.t.dt.to_period('Q')
    out=[]
    for p,g in df.groupby('q'):
        pf=g.r[g.r>0].sum()/max(1e-9,-g.r[g.r<0].sum()); out.append(f"{p}:n{len(g)} w{(g.r>0).mean():.0%} pf{pf:.2f}")
    return ' | '.join(out)
sym=sys.argv[1]
V=[('base bias1h rr3',dict()),('asia pool',dict(mode='asia')),('asia pool nobias',dict(mode='asia',bias=False)),('4h bias',dict(htf='4h')),
   ('NY only',dict(s_override=(13.0,17.0))),('London+NYopen',dict(s_override=(7.0,10.0)))]
for name,kw in V:
    a=dict(mode='orig',rr=3.0,bias=True,start='2025-07-01',end='2026-10-01',tf='m5',bpd=288,k=5,look_days=2,minstop=0.0003); a.update(kw)
    print(sym,name,'::',q(run(sym,**a)),flush=True)
