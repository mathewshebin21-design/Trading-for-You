"""H1 offline paper research only. No network, brokerage or production imports."""
import argparse
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import statistics
from paper_engine import PaperAccount, Rules, load_history, metrics
from strategy_lab import ComparisonAccount

WINDOWS = (('2016-01-01', '2025-12-31'), ('2021-01-01', '2025-12-31'),
           ('2026-01-01', '2026-09-30'))


def weight(closes):
    if len(closes) < 21:
        return None
    values = closes[-21:]
    if any(not math.isfinite(v) or v <= 0 for v in values):
        return None
    vol = statistics.stdev([b / a - 1 for a, b in zip(values, values[1:])]) * math.sqrt(252)
    return min(.25, .02 / vol) if vol > 0 and math.isfinite(vol) else None


class SizedAccount(PaperAccount):
    def __init__(self, rules, trend=True):
        super().__init__(rules)
        self.trend = trend
        self.cycle = None

    def rebalance(self, target, reference, day, reason):
        if not math.isfinite(target) or not 0 <= target <= .25:
            raise ValueError('Invalid capped target')
        r = self.rules
        equity = self.cash + self.units * reference
        gap = target * equity - self.units * reference
        side = 'BUY' if gap > 0 else 'SELL'
        friction = (r.spread_bps + r.slippage_bps) / 10000
        price = reference * (1 + friction if side == 'BUY' else 1 - friction)
        rate = r.commission_bps / 10000
        unit_cost = abs(price - reference) + price * rate
        if side == 'BUY':
            quantity = min(gap / (reference + target * unit_cost), self.cash / (price * (1 + rate)))
            quantity = math.floor(quantity / r.quantum) * r.quantum
        else:
            denominator = reference - target * unit_cost
            if denominator <= 0:
                raise ValueError('Costs incompatible with capped sizing')
            desired = max(0., self.units - (-gap) / denominator)
            remaining = math.floor(desired / r.quantum) * r.quantum
            quantity = self.units - remaining
        if quantity <= 1e-12:
            return
        if side == 'BUY' and self.units == 0:
            self.cycle = {'cash': self.cash, 'date': day}
        fee = quantity * price * rate
        if side == 'BUY':
            self.cash -= quantity * price + fee
            self.units += quantity
        else:
            self.cash += quantity * price - fee
            self.units = max(0., self.units - quantity)
            if self.units < 1e-12:
                self.units = 0.
                self.closed_trades.append({'net_pnl': self.cash - self.cycle['cash'],
                    'holding_days': (date.fromisoformat(day) - date.fromisoformat(self.cycle['date'])).days})
                self.cycle = None
        self.ledger.append({'date': day, 'side': side, 'quantity': quantity,
            'reference': reference, 'fill_price': price, 'commission': fee,
            'friction_cost': quantity * abs(price - reference), 'reason': reason})
        if self.cash < -1e-7 or self.units < 0:
            raise AssertionError('Borrowed cash or negative position')

    def step(self, bar, trade_enabled=True):
        # Validate the complete bar on a disposable account before any mutation.
        check = PaperAccount(self.rules)
        check.last_date = self.last_date
        check.step(bar, trade_enabled=False)
        if bar.get('distribution', 0) != 0:
            raise ValueError('Adjusted proxy must not also pay distributions')
        day = bar['date']
        week = date.fromisoformat(day).isocalendar()[:2]
        previous_week = date.fromisoformat(self.last_date).isocalendar()[:2] if self.last_date else None
        desired = weight(self.closes)
        bullish = self.target if self.trend else True
        if trade_enabled:
            if self.paused or not bullish or desired is None:
                self.rebalance(0., bar['open'], day, 'risk_or_bearish_or_invalid_exit')
            elif week != previous_week:
                self.rebalance(desired, bar['open'], day, 'weekly_lagged_weight')
            equity = self.cash + self.units * bar['close']
            self.peak = max(self.peak, equity)
            dd = equity / self.peak - 1
            self.curve.append({'date': day, 'equity': equity, 'cash': self.cash,
                'units': self.units, 'invested_during_bar': self.units > 0,
                'weight': self.units * bar['close'] / equity, 'drawdown': dd})
            if dd <= -self.rules.drawdown_pause:
                self.paused = True
        self.last_date = day
        self.closes = (self.closes + [bar['close']])[-100:]
        self.target = self.signal()


def evaluate(rows, calendar):
    dates = [r['date'] for r in rows]
    if not dates or dates != sorted(set(dates)) or dates != list(calendar):
        raise ValueError('Incomplete or unordered session calendar')
    if dates[-1] < WINDOWS[-1][1]:
        raise ValueError('Truncated requested history')
    results = []
    for start, end in WINDOWS:
        prior = [r for r in rows if r['date'] < start][-100:]
        measured = [r for r in rows if start <= r['date'] <= end]
        if len(prior) < 100 or not measured:
            raise ValueError('Insufficient warmup or measurement')
        for multiplier in (1, 2):
            rules = Rules(commission_bps=10 * multiplier, spread_bps=multiplier,
                          slippage_bps=5 * multiplier, quantum=.000001)
            for policy in ('fixed_sma', 'vol_sma', 'vol_without_trend', 'buy_hold_25', 'cash'):
                sized = policy in ('vol_sma', 'vol_without_trend')
                account = SizedAccount(rules, trend=policy == 'vol_sma') if sized else ComparisonAccount(
                    rules, {'fixed_sma': 'sma_20_100', 'buy_hold_25': 'buy_hold_25', 'cash': 'cash'}[policy])
                for bar in prior + measured:
                    enabled = bar['date'] >= start
                    if sized:
                        account.step(bar, trade_enabled=enabled)
                    else:
                        account.step(bar, trade_enabled=enabled, benchmark=policy == 'buy_hold_25',
                                     pause_enabled=policy not in ('buy_hold_25', 'cash'))
                weights = [p['units'] * r['close'] / p['equity'] for p, r in zip(account.curve, measured)]
                terminal = int(account.units > 0)
                last = measured[-1]
                if sized:
                    account.rebalance(0., last['close'], last['date'], 'terminal_measurement_close')
                else:
                    account.trade('SELL', last['close'], last['date'], 'terminal_measurement_close')
                account.curve[-1].update(equity=account.cash, cash=account.cash, units=0.)
                results.append({'start': start, 'end': end, 'policy': policy, 'cost_multiplier': multiplier,
                    'measured_sessions': len(measured), **metrics(account),
                    'fills': len(account.ledger), 'terminal_liquidations': terminal,
                    'natural_roundtrips': len(account.closed_trades) - terminal,
                    'mean_close_weight': statistics.mean(weights), 'maximum_close_weight': max(weights),
                    'turnover_notional_over_initial_capital': sum(t['quantity'] * t['reference'] for t in account.ledger) / rules.capital})
    return {'mode': 'H1_OFFLINE_KNOWN_HISTORY_ONLY', 'strategy_validated': False,
        'selected_strategy': None, 'model_trained': False, 'results': results,
        'limitations': ['Unverified adjusted snapshot; synthetic fractional units, not executable IEX fills.',
            'Overlapping inspected windows are development evidence, not independent holdouts.',
            '25% is a rebalance target cap; market drift can exceed it between rebalances.',
            '2% volatility budget is a sizing heuristic, not a risk guarantee.',
            'Cash interest/taxes excluded; benchmark risk controls differ as documented.',
            'No news, trader-copy feed or private production accounting tested.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('history', 'calendar', 'output'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    history, calendar, output = map(Path, (args.history, args.calendar, args.output))
    if output.resolve() in (history.resolve(), calendar.resolve()):
        raise ValueError('Output cannot overwrite input')
    result = evaluate(load_history(history), json.loads(calendar.read_text()))
    result['input_sha256'] = hashlib.sha256(history.read_bytes()).hexdigest()
    result['calendar_sha256'] = hashlib.sha256(calendar.read_bytes()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
