import pandas as pd, numpy as np
def ema(s,n): return s.ewm(span=n,adjust=False).mean()
SESS={'NQ':(13.5,20.0),'GOLD':(7.0,20.0)}
def run(sym, mode='orig', rr=3.0, bias=True, start='2025-07-01', end='2026-10-01', k=5, look_days=3, minstop=0.0004, tf='m15', bpd=96, htf='1h', s_override=None):
    m=pd.read_pickle(f'{sym}_{tf}.pkl')
    h1=m.resample('1h').agg({'close':'last'}).dropna(); h1['e']=ema(h1.close,50)
    trend=(h1.close>h1.e) if htf=='1h' else (h1.close.resample('4h').last().reindex(h1.index,method='ffill')>ema(h1.close.resample('4h').last().dropna(),50).reindex(h1.index,method='ffill')).astype(int)*2-1; trend=trend.shift(1).reindex(m.index,method='ffill')  # completed hour only
    day=m.index.floor('D'); dh=m.groupby(day).high.max(); dl=m.groupby(day).low.min()
    pdh=pd.Series(dh.shift(1).reindex(day).values,index=m.index); pdl=pd.Series(dl.shift(1).reindex(day).values,index=m.index)
    H=m.high.values; L=m.low.values; C=m.close.values; O=m.open.values; T=m.index; n=len(m)
    # pivots (confirmed k bars later)
    ph=np.full(n,np.nan); pl=np.full(n,np.nan)
    for i in range(k,n-k):
        if H[i]==H[i-k:i+k+1].max(): ph[i]=H[i]
        if L[i]==L[i-k:i+k+1].min(): pl[i]=L[i]
    s0,s1=s_override or SESS[sym]; hr=T.hour+T.minute/60
    i0=np.searchsorted(T,pd.Timestamp(start,tz='UTC')); i1=np.searchsorted(T,pd.Timestamp(end,tz='UTC'))
    trades=[]; i=max(i0,200); busy_until=-1
    lb=int(look_days*bpd)
    while i<i1-1:
        if i<=busy_until or not (s0<=hr[i]<s1): i+=1; continue
        tb=trend.iloc[i] if bias else 0
        # candidate levels
        if mode=='orig':
            js=np.arange(max(0,i-lb),i-k)
            sup=[pl[j] for j in js if not np.isnan(pl[j]) and L[j+1:i].min()>pl[j]] if len(js) else []
            res=[ph[j] for j in js if not np.isnan(ph[j]) and H[j+1:i].max()<ph[j]] if len(js) else []
        elif mode=='asia':
            dstart=np.searchsorted(T,T[i].floor('D')); aend=np.searchsorted(T,T[i].floor('D')+pd.Timedelta(hours=7 if sym=='GOLD' else 13.5))
            if i<=aend or aend<=dstart: i+=1; continue
            sup=[L[dstart:aend].min()]; res=[H[dstart:aend].max()]
            if L[aend:i].min()<=sup[0]: sup=[]
            if H[aend:i].max()>=res[0]: res=[]
        else:
            sup=[pdl.iloc[i]]; res=[pdh.iloc[i]]
            # level must be untouched today before this bar
            dstart=np.searchsorted(T,T[i].floor('D'))
            if dstart<i and L[dstart:i].min()<=sup[0]: sup=[]
            if dstart<i and H[dstart:i].max()>=res[0]: res=[]
        side=None
        if tb>=0 and sup:
            lv=max([s for s in sup if s<O[i]] or [np.nan])
            if not np.isnan(lv) and L[i]<lv and C[i]>lv: side=1
        if side is None and tb<=0 and res:
            lv=min([r for r in res if r>O[i]] or [np.nan])
            if not np.isnan(lv) and H[i]>lv and C[i]<lv: side=-1
        if side is None: i+=1; continue
        # entry on break of sweep candle within 3 bars
        trig=H[i] if side==1 else L[i]; sl=L[i] if side==1 else H[i]
        ent=None
        for j in range(i+1,min(i+4,i1)):
            if side==1 and L[j]<sl: break
            if side==-1 and H[j]>sl: break
            if (side==1 and H[j]>trig) or (side==-1 and L[j]<trig): ent=j; break
        if ent is None: i+=1; continue
        risk=abs(trig-sl)
        if risk<minstop*trig: i+=1; continue
        tp=trig+side*rr*risk; res_r=None
        dend=np.searchsorted(T,T[ent].floor('D')+pd.Timedelta(hours=21))
        for j in range(ent,min(dend,n)):
            hit_sl=(L[j]<=sl) if side==1 else (H[j]>=sl); hit_tp=(H[j]>=tp) if side==1 else (L[j]<=tp)
            if j==ent:  # on entry bar only count sl if bar extends beyond after trigger; conservative: sl first
                hit_tp = hit_tp and ((C[j]>=tp) if side==1 else (C[j]<=tp))
            if hit_sl: res_r=-1.0; ex=j; break
            if hit_tp: res_r=rr; ex=j; break
        if res_r is None:
            ex=min(dend,n)-1; res_r=side*(C[ex]-trig)/risk
        trades.append(dict(sym=sym,mode=mode,t=T[i],side=side,level=lv,entry=trig,sl=sl,tp=tp,r=res_r,exit_t=T[ex],risk_pts=risk))
        busy_until=ex; i=ex+1
    return pd.DataFrame(trades)
def summ(df):
    if not len(df): return 'none'
    w=(df.r>0).mean(); pf=df.r[df.r>0].sum()/max(1e-9,-df.r[df.r<0].sum())
    return f"n={len(df)} win={w:.0%} PF={pf:.2f} totR={df.r.sum():+.1f}"
if __name__=='__main__':
    Q=[('Q3-25','2025-07-01','2025-10-01'),('Q4-25','2025-10-01','2026-01-01'),('Q1-26','2026-01-01','2026-04-01'),('Q2-26','2026-04-01','2026-07-01'),('Q3-26','2026-07-01','2026-10-01')]
    for sym in ('NQ','GOLD'):
        for mode in ('orig','pdhl'):
            for q,a,b in Q:
                print(sym,mode,q,summ(run(sym,mode,start=a,end=b)))
