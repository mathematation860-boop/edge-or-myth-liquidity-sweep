import pandas as pd
B='/mnt/user-data/uploads/Gold-Trading-Assistant/data-dukascopy/'
def load(sym):
    if sym=='NQ':
        fs=[B+f'us100/US100_M1_bid_ask_{y}.parquet' for y in (2025,2026)]
    else:
        fs=[B+f'bid_ask/XAUUSD_M1_bid_ask_{y}.parquet' for y in (2025,2026)]
    d=pd.concat([pd.read_parquet(f) for f in fs])
    d['timestamp']=pd.to_datetime(d.timestamp,utc=True)
    d=d.set_index('timestamp')[['bid_open','bid_high','bid_low','bid_close']]; d.columns=['open','high','low','close']
    if sym=='GOLD':
        r=pd.read_csv(B+'XAUUSD_M1_recent.csv',parse_dates=['timestamp']).set_index('timestamp')[['open','high','low','close']]
        d=pd.concat([d,r]); d=d[~d.index.duplicated(keep='last')]
    return d.sort_index()
def rs(d,f): return d.resample(f).agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
if __name__=='__main__':
    for s in ('NQ','GOLD'):
        d=load(s); m=rs(d,'15min'); m.to_pickle(f'{s}_m15.pkl'); print(s, m.index[0], m.index[-1], len(m))
