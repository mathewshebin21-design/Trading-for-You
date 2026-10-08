"""Experiment 001. Deterministic historical/paper simulation only; no network/orders."""
from dataclasses import dataclass, field, asdict
from datetime import date
import csv
import math
import statistics


@dataclass(frozen=True)
class Rules:
    fast: int = 20
    slow: int = 100
    capital: float = 10000.0
    allocation: float = 0.25
    drawdown_pause: float = 0.10
    commission_bps: float = 1.0
    spread_bps: float = 1.0
    slippage_bps: float = 2.0
    quantum: float = 1.0
    crypto: bool = False

    def __post_init__(self):
        if not (0 < self.fast < self.slow and 0 < self.allocation <= 1 and
                self.capital > 0 and 0 < self.drawdown_pause < 1 and self.quantum > 0):
            raise ValueError('Invalid simulation rules')
        if not all(math.isfinite(v) for v in asdict(self).values()):
            raise ValueError('Non-finite rules')
        if min(self.commission_bps, self.spread_bps, self.slippage_bps) < 0:
            raise ValueError('Negative trading costs')
        if (self.spread_bps+self.slippage_bps)/10000 >= 1:
            raise ValueError('Invalid adverse execution costs')


def load_history(path, crypto=False):
    with open(path,newline='') as f:
        records=list(csv.DictReader(f))
    rows=[]
    previous=None
    for r in records:
        d=date.fromisoformat(r['Date'][:10])
        if previous and (d <= previous or (crypto and (d-previous).days != 1)):
            raise ValueError('Duplicate, unordered, or missing crypto dates')
        previous=d
        if float(r.get('Stock Splits',0) or 0) != 0:
            raise ValueError('Split dataset needs independent corporate-action review')
        row={'date':d.isoformat(), **{k:float(r[k.title()]) for k in ('open','high','low','close','volume')},
             'distribution':float(r.get('Dividends',0) or 0)+float(r.get('Capital Gains',0) or 0)}
        if not all(math.isfinite(v) for k,v in row.items() if k != 'date'):
            raise ValueError('Non-finite market data')
        if min(row['open'],row['low'],row['close']) <= 0 or row['volume'] < 0 or row['distribution'] < 0:
            raise ValueError('Invalid market data')
        if not row['low'] <= min(row['open'],row['close']) <= max(row['open'],row['close']) <= row['high']:
            raise ValueError('Invalid OHLC range')
        rows.append(row)
    if not rows: raise ValueError('No bars')
    return rows


@dataclass
class PaperAccount:
    rules: Rules
    cash: float = field(init=False)
    units: float = 0.0
    closes: list = field(default_factory=list)
    target: bool = False
    paused: bool = False
    peak: float = field(init=False)
    last_date: str = ''
    ledger: list = field(default_factory=list)
    curve: list = field(default_factory=list)
    entry: dict | None = None
    closed_trades: list = field(default_factory=list)

    def __post_init__(self):
        self.cash=self.rules.capital
        self.peak=self.rules.capital

    def signal(self):
        if len(self.closes) < self.rules.slow: return False
        return statistics.mean(self.closes[-self.rules.fast:]) > statistics.mean(self.closes[-self.rules.slow:])

    def trade(self, side, reference, day, reason):
        r=self.rules
        friction=(r.spread_bps+r.slippage_bps)/10000
        price=reference*(1+friction if side=='BUY' else 1-friction)
        rate=r.commission_bps/10000
        if side=='BUY':
            budget=min(self.cash,(self.cash+self.units*reference)*r.allocation)
            qty=math.floor(budget/(price*(1+rate))/r.quantum+1e-12)*r.quantum
            if qty <= 0: return
            fee=qty*price*rate
            outlay=qty*price+fee
            self.cash-=outlay
            self.units=qty
            self.entry={'date':day,'outlay':outlay,'distributions':0.0}
        else:
            qty=self.units
            if qty <= 0: return
            fee=qty*price*rate
            proceeds=qty*price-fee
            self.cash+=proceeds
            self.units=0.0
            self.closed_trades.append({'entry_date':self.entry['date'],'exit_date':day,
                'net_pnl':proceeds+self.entry['distributions']-self.entry['outlay'],
                'holding_days':(date.fromisoformat(day)-date.fromisoformat(self.entry['date'])).days})
            self.entry=None
        self.ledger.append({'date':day,'side':side,'quantity':qty,'reference':reference,
            'fill_price':price,'commission':fee,'friction_cost':qty*abs(price-reference),'reason':reason})
        if self.cash < -1e-7: raise AssertionError('Simulation borrowed cash')

    def step(self, bar, trade_enabled=True, benchmark=False, pause_enabled=True):
        """Process one chronological completed bar. Targets precede that bar's open."""
        day=bar['date']
        date.fromisoformat(day)
        values=[float(bar[k]) for k in ('open','high','low','close','volume')]
        distribution=float(bar.get('distribution',0))
        if not all(math.isfinite(v) for v in values+[distribution]):
            raise ValueError('Non-finite bar')
        if min(values[:4]) <= 0 or values[4]<0 or distribution<0:
            raise ValueError('Invalid bar')
        if not bar['low'] <= min(bar['open'],bar['close']) <= max(bar['open'],bar['close']) <= bar['high']:
            raise ValueError('Invalid OHLC range')
        if self.last_date and day <= self.last_date: raise ValueError('Bar already processed or out of order')
        if self.last_date and self.rules.crypto and (date.fromisoformat(day)-date.fromisoformat(self.last_date)).days != 1:
            raise ValueError('Missing crypto bar')
        self.last_date=day
        payout=self.units*bar.get('distribution',0)
        self.cash+=payout
        if self.entry: self.entry['distributions']+=payout
        if trade_enabled:
            desired=(not self.paused) and (True if benchmark else self.target)
            if desired and self.units==0: self.trade('BUY',bar['open'],day,'next_open' if not benchmark else 'benchmark_entry')
            elif not desired and self.units>0: self.trade('SELL',bar['open'],day,'drawdown_pause' if self.paused else 'next_open')
            equity=self.cash+self.units*bar['close']
            self.peak=max(self.peak,equity)
            dd=equity/self.peak-1
            self.curve.append({'date':day,'equity':equity,'cash':self.cash,'units':self.units,
                               'invested_during_bar':self.units>0,'drawdown':dd})
            if pause_enabled and dd <= -self.rules.drawdown_pause: self.paused=True
        self.closes.append(bar['close'])
        self.closes=self.closes[-self.rules.slow:]
        self.target=self.signal()
        return self.curve[-1] if trade_enabled else None

    def checkpoint(self):
        return asdict(self)

    @classmethod
    def restore(cls, record):
        account=cls(Rules(**record['rules']))
        for name,value in record.items():
            if name!='rules': setattr(account,name,value)
        return account


def replay(rows, rules, start, end, benchmark=False):
    a=PaperAccount(rules)
    eligible=[b for b in rows if b['date'] <= end]
    if not any(b['date'] >= start for b in eligible): raise ValueError('No measurement bars')
    for b in eligible:
        a.step(b,trade_enabled=b['date']>=start,benchmark=benchmark,pause_enabled=not benchmark)
    # Explicit terminal close is a measurement convention, not a forward signal.
    last=eligible[-1]
    a.trade('SELL',last['close'],last['date'],'terminal_measurement_close')
    a.curve[-1].update(equity=a.cash,cash=a.cash,units=0.0)
    return a


def metrics(account):
    eq=[account.rules.capital]+[p['equity'] for p in account.curve]
    returns=[b/a-1 for a,b in zip(eq,eq[1:])]
    frequency=365 if account.rules.crypto else 252
    std=statistics.stdev(returns) if len(returns)>1 else 0
    peak=eq[0]; worst=0.0
    for e in eq:
        peak=max(peak,e); worst=min(worst,e/peak-1)
    pnls=[t['net_pnl'] for t in account.closed_trades]
    gains=sum(p for p in pnls if p>0); losses=-sum(p for p in pnls if p<0)
    return {'net_return_pct':100*(eq[-1]/eq[0]-1),'maximum_drawdown_pct':100*worst,
        'annualized_volatility_pct':100*std*math.sqrt(frequency),
        'descriptive_sharpe_zero_cash_rate':statistics.mean(returns)/std*math.sqrt(frequency) if std else None,
        'closed_trades':len(pnls),'net_expectancy_dollars':statistics.mean(pnls) if pnls else None,
        'profit_factor':gains/losses if losses else None,
        'mean_holding_days':statistics.mean(t['holding_days'] for t in account.closed_trades) if pnls else None,
        'invested_bar_fraction':sum(p['invested_during_bar'] for p in account.curve)/len(account.curve),
        'modelled_cost_dollars':sum(t['commission']+t['friction_cost'] for t in account.ledger),
        'paused':account.paused,'evidence_status':'INSUFFICIENT_TRADE_COUNT' if len(pnls)<30 else 'EXPLORATORY_ONLY',
        'strategy_validated':False}
