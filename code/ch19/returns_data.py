"""Synthetic monthly returns for ten asset classes (NOT real market data).

A one-factor model with fat-tailed shocks: each asset responds to a common
market factor plus its own noise. 120 months = 10 years of history.
"""
import numpy as np

assets = ["Banks", "Telecom", "Energy", "Utilities", "Consumer",
          "Health", "Industry", "Tech", "GovBonds", "Gold"]
mu = np.array([0.80, 0.65, 0.90, 0.50, 0.70, 0.75, 0.80, 1.10, 0.30, 0.45])
beta = np.array([1.2, 0.8, 1.1, 0.5, 0.9, 0.7, 1.1, 1.4, -0.1, 0.1])
idio = np.array([3.5, 3.0, 5.0, 2.0, 2.8, 3.0, 3.5, 5.5, 1.0, 4.0])

rng = np.random.default_rng(60)
T = 120
market = 3.5 * rng.standard_t(df=4, size=T) / np.sqrt(2)   # % per month
noise = rng.standard_t(df=5, size=(T, len(assets))) / np.sqrt(5 / 3)
returns = mu + np.outer(market, beta) + noise * idio          # % per month
