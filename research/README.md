# Trading Research — Colab Starter

Research and paper trading only. No order-execution code is included.

## Best current setup

Use Google Colab Free on a CPU runtime for interactive research, and Google Drive for persistent notebooks and reports. No GPU, large language model or local Python installation is needed. Colab can disconnect and delete its temporary runtime; it is not reliable unattended hosting.

## Open the notebook

1. Open https://colab.research.google.com/.
2. Choose File → Upload notebook and select `Trading_Research_Colab.ipynb`.
3. Choose Runtime → Run all. The default run uses explicit synthetic fixtures and performs no network calls.
4. To fetch public crypto snapshots and official Federal Reserve news, set `FETCH_PUBLIC_DATA = True` and rerun.
5. To collect small historical research samples, set `DOWNLOAD_HISTORY = True` and rerun. This optional step installs yfinance in the cloud runtime. These data are not a verified real-time feed.
6. To preserve outputs in your Google account, set `SAVE_TO_DRIVE = True`. Colab will request Drive authorization. It creates a new timestamped folder for each run under `MyDrive/TradingResearch/runs`.

If Drive is disabled, download the generated results ZIP before the runtime ends. There is no background process after a session disconnects. The notebook is self-contained: no project-folder upload is required. You need to sign into your own Google account to open a runtime; this delivery has not created or run one in your account.

## Included files

- `Trading_Research_Colab.ipynb`: runnable cloud research workbench.
- `research_workbench.py`: standalone source embedded in the notebook.
- `PROJECT.md`: nine-stage project specification and evidence standards.
- `BUILD_STATUS.json`: exact implemented, tested and pending capabilities.

## Verification performed

All default notebook code cells were executed in order using Python in the build environment. Eight targeted checks passed for OHLC integrity, duplicate dates, endpoint isolation, quote timestamp honesty, crossed quotes, publication-versus-observation time and copy eligibility defaults. No performance result was generated.

Optional network calls, yfinance downloads, Drive mounting and the actual Google Colab runtime were not tested here. API outages, regional restrictions and provider changes can affect these steps. Errors are reported without silently substituting synthetic data.

## Current limits

Update: Experiment 001 adds a fixed-rule backtester, a resumable historical paper-account simulator and an executed Colab experiment notebook. Twelve accounting/timing tests passed. All 80 predefined comparisons completed, but holdout evidence is insufficient (2–3 completed trades per instrument). This does not connect a prospective feed or validate a strategy. See EXPERIMENT_001.md and experiment_001_results/REPORT.md.

### Initial workbench limits (superseded for the baseline simulator)

No validated strategy, paper simulator, continuous collector, verified trader-copy source or news prediction model exists yet. US stock and gold real-time feeds remain unselected. GLD is only a provisional gold proxy. News coverage is limited to one primary macro publisher. Historical convenience symbols are not an unbiased historical investment universe.

The optional historical downloader logs its installed dependency version and retains downloaded bytes/checksums. Before controlled strategy experiments, select and pin an audited version, resolve data rights and accounting conventions, freeze the universe, costs, rules, evaluation dates and risk limits. Do not interpret successful notebook execution as evidence of a trading edge.

## Storage

The delivered starter is small. Its default run produces small JSON reports. Optional downloads and later archives consume cloud runtime storage and, if saved, Google Drive quota. It imposes no large installation on your device. Avoid tick data or model weights until their value has been established.

## References

- https://research.google.com/colaboratory/faq.html
- https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md
- https://github.com/ranaroussi/yfinance
- https://www.federalreserve.gov/feeds/feeds.htm


Experiment 002: see EXPERIMENT_002.md, DEDICATED_SYSTEM.md and experiment_002_results/REPORT.md. Run the self-contained Trading_Research_Experiment_002.ipynb in Colab for historical tests and interactive public-feed paper observations. All strategies remain unvalidated. No continuous deployment or live-order code.

Telegram paper control: see TELEGRAM_SETUP.md. Built and offline tested; requires a dedicated bot, secure token, owner pairing and Linux hosting before activation. Manual trades remain separate from strategy research.
