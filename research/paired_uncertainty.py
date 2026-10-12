"""Offline paper research: descriptive paired block-bootstrap intervals only.

Input equities must be net of costs, reconciled, equally timestamped and free
of external cash flows. expected_dates must come from an independent calendar
review, including the initial mark. This module cannot certify those premises.
No strategy selection, profitability certification, network or execution.
"""
import math
import random
import statistics
from datetime import date


def paired_interval(observations, expected_dates, block_length=5, samples=2000, seed=0):
    if (type(block_length) is not int or block_length < 1 or
            type(samples) is not int or not 100 <= samples <= 10000 or
            type(seed) is not int):
        raise ValueError('Invalid bootstrap configuration')
    dates = list(expected_dates)
    if len(dates) < 3 or dates != sorted(set(dates)):
        raise ValueError('Expected dates must be unique and chronological')
    for day in dates:
        if date.fromisoformat(day).isoformat() != day:
            raise ValueError('Expected dates must be canonical ISO dates')
    if [row['date'] for row in observations] != dates:
        raise ValueError('Missing, extra, duplicate or unordered comparison marks')
    for row in observations:
        if row.get('valid') is not True:
            raise ValueError('Invalid coverage or accounting mark')
        for key in ('strategy_equity', 'benchmark_equity'):
            value = row[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError('Require finite positive numeric equities')
    excess = [
        new['strategy_equity'] / old['strategy_equity'] -
        new['benchmark_equity'] / old['benchmark_equity']
        for old, new in zip(observations, observations[1:])
    ]
    if not all(math.isfinite(value) for value in excess):
        raise ValueError('Non-finite return')
    n = len(excess)
    if n < 2 * block_length:
        raise ValueError('Require at least two blocks of paired returns')
    rng = random.Random(seed)
    means = []
    # Circular moving blocks retain local dependence and equal series length.
    for _ in range(samples):
        draw = []
        while len(draw) < n:
            start = rng.randrange(n)
            draw.extend(excess[(start + offset) % n] for offset in range(block_length))
        means.append(statistics.mean(draw[:n]))
    means.sort()
    def quantile(p):
        position = (samples - 1) * p
        low = math.floor(position)
        high = math.ceil(position)
        return means[low] + (means[high] - means[low]) * (position - low)
    return {
        'mode': 'OFFLINE_PAPER_RESEARCH', 'paired_returns': n,
        'block_length': block_length, 'samples': samples, 'seed': seed,
        'mean_daily_excess_return': statistics.mean(excess),
        'descriptive_95pct_percentile_interval': [quantile(.025), quantile(.975)],
        'strategy_validated': False, 'selected_strategy': None,
        'limitations': [
            'Short samples and nonstationarity can make intervals unreliable.',
            'No multiple-testing or selection-bias correction is applied.',
            'Prespecify block lengths; report sensitivity without choosing the best interval.',
            'Calendar completeness, equal mark times and no cash flows require independent review.',
            'This estimates mean daily relative returns, not terminal dollar excess or live profits.',
        ],
    }
