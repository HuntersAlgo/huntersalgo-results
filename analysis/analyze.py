"""Summarise the published HunterML test files and draw three charts.

Reads hunterml/excursions/*.csv, writes analysis/README.md and analysis/*.png.
Every number is a hypothetical replay result for one NQ contract.

    python analysis/analyze.py            # as published, no trading costs
    python analysis/analyze.py --cost 10  # subtract 10 USD per round turn

Needs pandas and matplotlib.
"""
import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "analysis"

# The six distinct runs. 05 and 06 repeat 02, 08 repeats 07, 10 repeats 09.
RUNS = {
    "01": "Two-sided, news hours blocked",
    "02": "Two-sided baseline (control)",
    "03": "News blocked, short stop 160",
    "04": "News blocked, short stop 180",
    "07": "Conservative long-only (60/45)",
    "09": "Low-drawdown long-only",
}

SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, BLUE, ORANGE = "#e1e0d9", "#c3c2b7", "#2a78d6", "#eb6834"

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 10,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": INK,
})


def load(num, cost):
    df = pd.read_csv(ROOT / "hunterml" / "excursions" / f"template-{num}-excursions.csv")
    df["exit_time"] = pd.to_datetime(df["exit_time"])
    df = df.sort_values("exit_time").reset_index(drop=True)
    df["pnl"] = df["pnl_currency"] - cost
    df["equity"] = df["pnl"].cumsum()
    df["drawdown"] = df["equity"] - df["equity"].cummax().clip(lower=0)
    return df


def stats(df):
    wins, losses = df.loc[df.pnl > 0, "pnl"].sum(), -df.loc[df.pnl < 0, "pnl"].sum()
    return {
        "trades": len(df),
        "win_rate": (df.pnl > 0).mean() * 100,
        "net": df.pnl.sum(),
        "pf": wins / losses if losses else float("nan"),
        "max_dd": df.drawdown.min(),
    }


def usd(v):
    return f"-${abs(v):,.0f}" if v < 0 else f"${v:,.0f}"


def style(ax):
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0, labelsize=9)
    ax.yaxis.set_major_formatter(lambda v, _: usd(v))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))


def small_multiples(data, column, title, note, filename, fill):
    fig, axes = plt.subplots(3, 2, figsize=(10, 10.5), sharex=True, sharey=True)
    for ax, (num, df) in zip(axes.flat, data.items()):
        style(ax)
        x, y = df["exit_time"], df[column]
        ax.step(x, y, where="post", color=BLUE, linewidth=2)
        if fill:
            ax.fill_between(x, y, 0, step="post", color=BLUE, alpha=0.18, linewidth=0)
        ax.axhline(0, color=AXIS, linewidth=1)
        ax.set_title(f"{num}  {RUNS[num]}", loc="left", fontsize=11, fontweight="bold", color=INK, pad=8)
        value = y.min() if fill else y.iloc[-1]
        label = f"Deepest {usd(value)}" if fill else f"Ends {usd(value)}"
        ax.text(0.02, 0.06 if fill else 0.9, label, transform=ax.transAxes, fontsize=10, color=INK2)
    fig.suptitle(title, x=0.06, y=0.985, ha="left", fontsize=15, fontweight="bold")
    fig.text(0.06, 0.95, note, ha="left", fontsize=10, color=INK2)
    fig.tight_layout(rect=(0.03, 0.01, 0.98, 0.94), h_pad=2.2)
    fig.savefig(OUT / filename, dpi=160)
    plt.close(fig)


def excursion_scatter(df, note, filename):
    fig, ax = plt.subplots(figsize=(10, 6.4))
    style(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.xaxis.set_major_locator(matplotlib.ticker.AutoLocator())
    ax.xaxis.set_major_formatter(lambda v, _: usd(v))
    for label, mask, colour in (("Closed at a profit", df.pnl > 0, BLUE), ("Closed at a loss", df.pnl <= 0, ORANGE)):
        part = df[mask]
        ax.scatter(part["mae_currency"], part["mfe_currency"], s=44, color=colour,
                   edgecolor=SURFACE, linewidth=1, label=f"{label} ({len(part)})")
    ax.set_xlabel("Worst point against the trade (MAE), USD")
    ax.set_ylabel("Best point in favour of the trade (MFE), USD")
    ax.legend(frameon=False, loc="upper right", fontsize=10, labelcolor=INK2)
    fig.suptitle("Template 01: how far each trade went for and against", x=0.06, y=0.97, ha="left",
                 fontsize=15, fontweight="bold")
    fig.text(0.06, 0.915, note, ha="left", fontsize=10, color=INK2)
    fig.tight_layout(rect=(0.03, 0.01, 0.98, 0.9))
    fig.savefig(OUT / filename, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cost", type=float, default=0.0, help="USD to subtract per round-turn trade")
    cost = parser.parse_args().cost
    basis = "before commission and slippage" if cost == 0 else f"after {usd(cost)} per round turn"
    note = f"Hypothetical market replay, one NQ contract, {basis}. Not live results."

    data = {num: load(num, cost) for num in RUNS}
    small_multiples(data, "equity", "Cumulative result by trade, six HunterML runs", note, "equity.png", fill=False)
    small_multiples(data, "drawdown", "Drawdown from the running peak, six HunterML runs", note, "drawdown.png", fill=True)
    excursion_scatter(data["01"], note, "excursions-template-01.png")

    rows = ["| Run | Configuration | Trades | Win rate | Net | Profit factor | Max drawdown |",
            "| --- | --- | --- | --- | --- | --- | --- |"]
    for num, df in data.items():
        s = stats(df)
        rows.append(f"| {num} | {RUNS[num]} | {s['trades']} | {s['win_rate']:.2f}% | {usd(s['net'])} | "
                    f"{s['pf']:.2f} | {usd(s['max_dd'])} |")

    text = f"""# Analysis of the published HunterML files

**Hypothetical market replay results.** One NQ contract, {basis}, 1 May to 26 June 2026. None of this is a live trading record. Read the [limits in the main README](../README.md#read-this-before-using-the-numbers) first.

Everything on this page is produced by [`analyze.py`](analyze.py) from the CSV files in [`hunterml/excursions/`](../hunterml/excursions). It covers the six distinct runs. Templates 05, 06, 08 and 10 are reruns of 02, 07 and 09, so they are left out.

## Summary

{chr(10).join(rows)}

Drawdown is measured on closed trades, from the running peak of cumulative result, starting at zero.

## Cumulative result

![Cumulative result by trade for six HunterML runs, as small panels sharing one scale](equity.png)

## Drawdown

![Drawdown from the running peak for six HunterML runs, as small panels sharing one scale](drawdown.png)

## Excursions, template 01

Each dot is one trade. Further right means the trade went further against the position before it closed. Higher means it went further in favour.

![Scatter of maximum adverse against maximum favourable excursion for template 01, split by trades closed at a profit and at a loss](excursions-template-01.png)

## Run it with trading costs

The published files carry no commission and no slippage. To see the same tables and charts with a cost taken off every trade:

```
python analysis/analyze.py --cost 10
```

That rewrites this page and the three images using the cost you give it. Use your own broker's round-turn figure.

## Disclosure

Hypothetical performance results have many inherent limitations. No representation is being made that any account will or is likely to achieve profits or losses similar to those shown. The full disclosure is in the [main README](../README.md#disclosures). Futures trading involves substantial risk of loss and is not suitable for every investor.
"""
    (OUT / "README.md").write_bytes(text.encode("utf-8"))
    print(text.split("## Cumulative")[0])


if __name__ == "__main__":
    main()
