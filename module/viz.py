# module/viz.py

import numpy as np
import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt




def plot_weights(portfolio):
    lim = 1e-3
    weights_df = portfolio["opt_portfolio"]['w']
    bench_weights = portfolio["bench_portfolio"]['w']
    portfolio_w = weights_df[weights_df["w"] > lim].copy()
    # Figure
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    # Optimized Portfolio
    sns.barplot(data=portfolio_w, x=portfolio_w.index,
        y="w", color="gray", ax=axes[0])
    axes[0].set_title("Optimized Portfolio Weights")
    axes[0].set_xlabel("Assets")
    axes[0].set_ylabel("Weight")
    plt.setp(axes[0].get_xticklabels(), rotation=30, ha='right')
    # Benchmark Portfolio
    benchmark_w = bench_weights[bench_weights["w"] > lim].copy()
    sns.barplot(data=benchmark_w, x=benchmark_w.index,
        y="w", color="steelblue", ax=axes[1])
    axes[1].set_title("Benchmark Weights")
    axes[1].set_xlabel("Assets")
    axes[1].set_ylabel("Weight")
    plt.setp(axes[1].get_xticklabels(), rotation=30, ha='right')
    plt.tight_layout()
    return fig, axes



def plot_performance(portfolio, title="Portfolio Performance vs. Benchmark"):
    opt_portfolio = portfolio['opt_portfolio']['portfolio']
    benchmark = portfolio['bench_portfolio']['portfolio']
    # Daily / periodic returns 
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    axes[0].plot(opt_portfolio.index, opt_portfolio["ret"], label="Optimized Portfolio", alpha=0.7)
    axes[0].plot(benchmark.index, benchmark["ret"], label="Benchmark", alpha=0.7)
    axes[0].set_title("Portfolio Returns")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Return")
    axes[0].legend()
    axes[0].grid(True)
    # Cumulative returns 
    axes[1].plot(opt_portfolio.index, opt_portfolio["cum_ret"], label="Optimized Portfolio", alpha=0.7)
    axes[1].plot(benchmark.index, benchmark["cum_ret"], label="Benchmark", alpha=0.7)
    axes[1].set_title("Cumulative Returns")
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Cumulative Return")
    axes[1].legend()
    axes[1].grid(True)
    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    return fig, axes



def plot_portfolio_metrics(portfolio):
    # Metrics comparison
    metrics_df = pd.DataFrame({
        "Optimized Portfolio": portfolio['opt_portfolio']['metrics'],
        "Benchmark": portfolio['bench_portfolio']['metrics']
    }).T
    metrics_order = ["Return", "Volatility", "Sharpe Ratio",
        "Tracking Error", "ITR", "Climate VaR",
        "Physical Risk","Diversification Ratio"
    ]
    metrics_df = metrics_df[metrics_order]
    # Plot
    fig, ax = plt.subplots(figsize=(14, 5))
    x = np.arange(len(metrics_order))
    width = 0.35
    ax.bar(x - width/2, metrics_df.loc["Optimized Portfolio"],
        width=width,label="Optimized Portfolio")
    ax.bar(x + width/2, metrics_df.loc["Benchmark"],
        width=width, label="Benchmark")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_order, rotation=20)
    ax.set_ylabel("Metric Value")
    ax.set_title("Portfolio vs Benchmark Metrics")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    return fig, ax



# Combined dashboard
def plot_dashboard_portfolio(portfolio, title="Portfolio Optimization Dashboard"):
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.1])
    # Weights
    fig_w, axes_w = plot_weights(portfolio)
    for i, ax in enumerate(axes_w):
        target_ax = fig.add_subplot(gs[0, i])
        # Copy bars
        for container in ax.containers:
            target_ax.bar([p.get_x() + p.get_width()/2 for p in container],
                [p.get_height() for p in container],
                width=[p.get_width() for p in container], alpha=0.8)
        target_ax.set_title(ax.get_title())
        target_ax.set_xlabel(ax.get_xlabel())
        target_ax.set_ylabel(ax.get_ylabel())
        target_ax.set_xticks(ax.get_xticks())
        target_ax.set_xticklabels( [t.get_text() for t in ax.get_xticklabels()],
            rotation=30, ha="right")
    plt.close(fig_w)
    # Performance
    fig_p, axes_p = plot_performance(portfolio)
    for i, ax in enumerate(axes_p):
        target_ax = fig.add_subplot(gs[1, i])
        # Copy lines
        for line in ax.lines:
            target_ax.plot(line.get_xdata(), line.get_ydata(),
                label=line.get_label(), alpha=0.7)
        target_ax.set_title(ax.get_title())
        target_ax.set_xlabel(ax.get_xlabel())
        target_ax.set_ylabel(ax.get_ylabel())
        target_ax.grid(True, alpha=0.3)
        target_ax.legend()
    plt.close(fig_p)
    # Metrics
    fig_m, ax_m = plot_portfolio_metrics(portfolio)
    target_ax = fig.add_subplot(gs[2, :])
    # Copy bars
    for container in ax_m.containers:
        target_ax.bar([p.get_x() + p.get_width()/2 for p in container],
            [p.get_height() for p in container],
            width=[p.get_width() for p in container], alpha=0.8)
    target_ax.set_title(ax_m.get_title())
    target_ax.set_ylabel(ax_m.get_ylabel())
    target_ax.set_xticks(ax_m.get_xticks())
    target_ax.set_xticklabels([t.get_text() for t in ax_m.get_xticklabels()], rotation=20)
    target_ax.grid(axis="y", alpha=0.3)
    target_ax.legend(["Optimized Portfolio", "Benchmark"])
    plt.close(fig_m)
    fig.suptitle(title, fontsize=20, y=0.98)
    plt.tight_layout()
    plt.show()



# Efficient Frontier Plotting
def plot_efficient_frontier(
    frontiers,
    portfolio_dict=None, cov=None, mu=None, 
    title=""
):
    frontier_returns, frontier_risks  = frontiers
    # get metrics
    opt_return = portfolio_dict["opt_portfolio"]["metrics"]["Return"]
    opt_risk = portfolio_dict["opt_portfolio"]["metrics"]["Volatility"]
    bench_return = portfolio_dict["bench_portfolio"]["metrics"]["Return"]
    bench_risk = portfolio_dict["bench_portfolio"]["metrics"]["Volatility"]
    # Issuers
    asset_returns = mu.values
    asset_risks = np.sqrt(np.diag(cov.values))
    # figure
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.scatter(frontier_risks, frontier_returns, s=60, zorder=3)
    ax.plot(frontier_risks, frontier_returns, linewidth=1.5, alpha=0.8, zorder=2)
    # Optimized portfolio
    ax.scatter(opt_risk, opt_return, s=200, zorder=4, 
        marker='*', label='Optimized Portfolio', color='red')
    # Benchmark portfolio
    ax.scatter(bench_risk, bench_return, s=200, zorder=4, 
        marker='*', label='Benchmark Portfolio', color='green')
    # Individual assets
    ax.scatter(asset_risks, asset_returns, s=45, alpha=0.7, label="Assets", zorder=1)
    ax.set_xlabel("Volatility")
    ax.set_ylabel("Expected Return")
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    return fig, ax


def plot_multiple_frontiers(
    frontiers_dict,
    title="Efficient Frontier Comparison"
):
    fig, ax = plt.subplots(figsize=(11, 6))
    for label, frontier in frontiers_dict.items():
        frontier_returns, frontier_risks = frontier
        ax.plot(frontier_risks, frontier_returns, linewidth=2, label=label)
        ax.scatter(frontier_risks, frontier_returns, s=35, alpha=0.7)
    ax.set_title(title)
    ax.set_xlabel("Volatility")
    ax.set_ylabel("Expected Return")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    return fig, ax