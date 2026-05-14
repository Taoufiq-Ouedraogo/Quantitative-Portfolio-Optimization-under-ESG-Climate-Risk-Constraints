# module/utils.py

import numpy as np
import pandas as pd




def portfolio_metrics(
    w, 
    mu=None, cov=None, 
    physical=None, itr=None, cvar=None
):
    w = np.array(w)
    # Core financials
    ret = float(mu.values @ w)
    vol = float(np.sqrt(w.T @ cov.values @ w))
    # Risk-adjusted performance
    sharpe = ret / vol if vol > 0 else 0.0
    # Tracking error (if benchmark provided)
    w_b = np.ones_like(w) / len(w)
    d = w - w_b
    tracking_error = float(np.sqrt(d.T @ cov.values @ d))
    # Concentration metrics
    max_weight = float(np.max(w))
    # Diversification ratio (classic quant metric)
    individual_vol = np.sqrt(np.diag(cov.values))
    weighted_avg_vol = float(w @ individual_vol)
    diversification_ratio = weighted_avg_vol / vol if vol > 0 else 0.0
    return {
        # Financial
        "Return": ret, "Volatility": vol, "Sharpe Ratio": sharpe,
        # Active risk
        "Tracking Error": tracking_error,
        # Climate
        "ITR": float(itr.values @ w), "Climate VaR": float(cvar.values @ w),
        "Physical Risk": float(physical.values @ w),
        # Portfolio structure
        "Max Weight": max_weight, "Diversification Ratio": diversification_ratio,
    }



def get_portfolio(
    w, 
    assets=None, returns=None, 
    mu=None, cov=None, 
    physical=None, itr=None, cvar=None,
    benchmark_=None
):
    # optimized weights
    weights_df = pd.DataFrame(w, columns=["w"], index=assets)
    weights_df = weights_df.sort_values("w", ascending=False)
    weights_df[weights_df["w"] <= 1e-4] = 0
    weights_df["w"] /= weights_df["w"].sum()
    # benchmark weights
    weights_bench = weights_df.copy()
    weights_bench["w"] = 1 / len(weights_df)
    # portfolio returns
    portfolio = pd.DataFrame(index=returns.index)
    portfolio["ret"] = returns[assets] @ weights_df["w"]
    portfolio["cum_ret"] = (1 + portfolio["ret"]).cumprod()
    # benchmark returns
    benchmark = benchmark_.set_index("Date").copy()
    benchmark["ret"] = benchmark["Cours"].pct_change()
    benchmark["cum_ret"] = (1 + benchmark["ret"]).cumprod()
    # portfolio metrics
    opt_metrics = portfolio_metrics(
        w=weights_df["w"], mu=mu, cov=cov, 
        physical=physical, itr=itr, cvar=cvar
    )
    # portfolio metrics
    bench_metrics = portfolio_metrics(
        w=weights_bench["w"], mu=mu, cov=cov, 
        physical=physical, itr=itr, cvar=cvar
    )
    # results
    opt_portfolio = {"w": weights_df, "portfolio": portfolio, "metrics": opt_metrics}
    bench_portfolio = {"w": weights_bench, "portfolio": benchmark, "metrics": bench_metrics}
    return {"opt_portfolio": opt_portfolio, "bench_portfolio": bench_portfolio}