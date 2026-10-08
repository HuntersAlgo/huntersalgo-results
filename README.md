# HuntersAlgo published test files

The trade logs behind the figures on the [HuntersAlgo results page](https://huntersalgo.com/results), in one place so they can be downloaded and checked.

**Every file here is a hypothetical result.** None of it is a live trading record, and none of it is a customer's account. The HunterML files come from NinjaTrader 8 market replay and Strategy Analyzer runs. The HunterBreakOut file comes from a Strategy Analyzer backtest.

All 21 files are byte-identical copies of the ones served at `huntersalgo.com/results/`.

## What is in here

| Folder | Files | What it is |
| --- | --- | --- |
| [`hunterml/trades/`](hunterml/trades) | 10 CSV | One row per trade for each of the ten HunterML templates |
| [`hunterml/excursions/`](hunterml/excursions) | 10 CSV | The same trades with exit price, MAE, MFE, stop and target |
| [`hunterbreakout/`](hunterbreakout) | 1 JSON | The HunterBreakOut backtest trade log |
| [`analysis/`](analysis) | Script, 3 charts | Summary table, cumulative result, drawdown and excursion charts built from the CSVs |

## HunterML templates

Ten configurations of [HunterML](https://huntersalgo.com/strategies/hunterml), all on the NQ continuous contract, all over the same window. 2,796 logged trades in total.

| # | Configuration | Direction | Trades | First entry | Last entry | Files |
| --- | --- | --- | --- | --- | --- | --- |
| 01 | Two-sided model, news hours blocked | Two-sided | 373 | 1 May 2026 | 26 Jun 2026 | [trades](hunterml/trades/template-01-trades.csv) · [excursions](hunterml/excursions/template-01-excursions.csv) |
| 02 | Two-sided baseline (control run) | Two-sided | 436 | 1 May 2026 | 26 Jun 2026 | [trades](hunterml/trades/template-02-trades.csv) · [excursions](hunterml/excursions/template-02-excursions.csv) |
| 03 | News hours blocked, tighter short stop (160) | Two-sided | 374 | 1 May 2026 | 26 Jun 2026 | [trades](hunterml/trades/template-03-trades.csv) · [excursions](hunterml/excursions/template-03-excursions.csv) |
| 04 | News hours blocked, wider short stop (180) | Two-sided | 373 | 1 May 2026 | 26 Jun 2026 | [trades](hunterml/trades/template-04-trades.csv) · [excursions](hunterml/excursions/template-04-excursions.csv) |
| 05 | Two-sided baseline, reproducibility rerun | Two-sided | 436 | 1 May 2026 | 26 Jun 2026 | [trades](hunterml/trades/template-05-trades.csv) · [excursions](hunterml/excursions/template-05-excursions.csv) |
| 06 | Two-sided best-net config, reproducibility rerun | Two-sided | 436 | 1 May 2026 | 26 Jun 2026 | [trades](hunterml/trades/template-06-trades.csv) · [excursions](hunterml/excursions/template-06-excursions.csv) |
| 07 | Conservative long-only profile (60/45) | Long only | 63 | 1 May 2026 | 25 Jun 2026 | [trades](hunterml/trades/template-07-trades.csv) · [excursions](hunterml/excursions/template-07-excursions.csv) |
| 08 | Conservative long-only profile, confirmation rerun | Long only | 63 | 1 May 2026 | 25 Jun 2026 | [trades](hunterml/trades/template-08-trades.csv) · [excursions](hunterml/excursions/template-08-excursions.csv) |
| 09 | Low-drawdown long-only profile | Long only | 121 | 1 May 2026 | 26 Jun 2026 | [trades](hunterml/trades/template-09-trades.csv) · [excursions](hunterml/excursions/template-09-excursions.csv) |
| 10 | Production candidate, low-drawdown long-only | Long only | 121 | 1 May 2026 | 26 Jun 2026 | [trades](hunterml/trades/template-10-trades.csv) · [excursions](hunterml/excursions/template-10-excursions.csv) |

Templates 05 and 06 repeat 02, 08 repeats 07, and 10 repeats 09. The reruns are kept so the repeatability of each run can be checked. They are not extra evidence.

## Read this before using the numbers

- **One contract, no costs.** In every row of the excursion files, `pnl_currency` equals the price move times $20 per point. That is one NQ contract with no commission and no slippage deducted. Real trading pays both.
- **Eight weeks.** Every HunterML run covers the same window of roughly eight weeks. That is a short sample of one market period.
- **Ten configurations, one window.** The results page highlights the best of the ten. Picking the best run after the fact is hindsight, which is why all ten are published here and not only the first.
- **Replay is not execution.** Market replay and backtests cannot fully model partial fills, latency, connection drops or gap days.

The [methodology](https://huntersalgo.com/methodology), the [backtesting vs live guide](https://huntersalgo.com/guides/backtesting-vs-live-trading-results) and the [disclosures](https://huntersalgo.com/disclosures) cover these limits in more detail.

## File formats

### `hunterml/trades/template-NN-trades.csv`

| Column | Meaning |
| --- | --- |
| `audit_run_id` | Label of the saved test run. `none` where the run was saved without one |
| `decision_id` | Identifier the strategy logged for the entry decision |
| `entry_time`, `exit_time` | Timestamps as exported by NinjaTrader. No timezone offset is recorded in the file |
| `entry_signal` | `MLLong` or `MLShort` |
| `entry_price` | Entry fill price in the replay |
| `pnl_currency` | Trade result in USD for one contract, before commission and slippage |
| `model_version` | Identifier of the model file used for the run |
| `model_signal`, `model_confidence` | Model output as logged by the strategy at the entry decision |
| `exit_price` | Exit fill price in the replay, taken from the matching excursions file |
| `direction` | `Long` or `Short`, the same side as `entry_signal` |
| `quantity` | Contracts traded. Always `1` (one NQ contract) |

### `hunterml/excursions/template-NN-excursions.csv`

The same trades. It has the trade columns except `direction` and `quantity`, plus:

| Column | Meaning |
| --- | --- |
| `mae_ticks`, `mae_currency` | Maximum adverse excursion during the trade |
| `mfe_ticks`, `mfe_currency` | Maximum favourable excursion during the trade |
| `initial_stop_ticks`, `target_ticks` | Stop and target distance set at entry |

### `hunterbreakout/hunterbreakout-trades.json`

An array of 533 trades from a Strategy Analyzer backtest of [HunterBreakOut](https://huntersalgo.com/strategies/hunterbreakout) on NQ 06-26, one contract, first entry 3 March 2025, last exit 10 April 2026. Fields: `num`, `instrument`, `direction`, `qty`, `entryPrice`, `exitPrice`, `entryTime`, `exitTime`, `entryName`, `exitName`, `profit`, `cumProfit`. Losses in `profit` are written in brackets, for example `($305.00)`.

## Check it yourself

```python
import csv, glob

for path in sorted(glob.glob("hunterml/excursions/*.csv")):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    total = sum(float(r["pnl_currency"]) for r in rows)
    mismatched = sum(
        abs((float(r["exit_price"]) - float(r["entry_price"])) * 20
            * (1 if r["entry_signal"] == "MLLong" else -1)
            - float(r["pnl_currency"])) > 0.01
        for r in rows
    )
    print(path, len(rows), "trades", total, "USD before costs", mismatched, "rows off")
```

Each file should report zero rows off.

The other eleven strategies in the suite do not have published result packages yet, so there is nothing for them here.

## Disclosures

Hypothetical performance results have many inherent limitations, some of which are described below. No representation is being made that any account will or is likely to achieve profits or losses similar to those shown; in fact, there are frequently sharp differences between hypothetical performance results and the actual results subsequently achieved by any particular trading program. One of the limitations of hypothetical performance results is that they are generally prepared with the benefit of hindsight. In addition, hypothetical trading does not involve financial risk, and no hypothetical trading record can completely account for the impact of financial risk of actual trading. For example, the ability to withstand losses or to adhere to a particular trading program in spite of trading losses are material points which can also adversely affect actual trading results. There are numerous other factors related to the markets in general or to the implementation of any specific trading program which cannot be fully accounted for in the preparation of hypothetical performance results and all which can adversely affect trading results.

Futures trading involves substantial risk of loss and is not suitable for every investor. Past performance is not indicative of future results. HuntersAlgo sells software and does not provide financial advice.

<sub>NinjaTrader® is a registered trademark of NinjaTrader Group, LLC. No NinjaTrader company has any affiliation with the owner, developer, or provider of the products or services described herein, or any interest, ownership or otherwise, in any such product or service, or endorses, recommends or approves any such product or service.</sub>
