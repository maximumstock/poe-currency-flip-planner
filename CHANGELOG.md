# 0.3.6 / 2021-01-18

- Update cli.py to default to `Ritual` softcore league

# 0.3.5 / 2021-01-15

- Update assets.json with all supported item meta data for Ritual league
- Fix pyproject.toml dependencies and update requirements.txt

# 0.3.4 / 2021-01-10

- Fix config file path resolution.

# 0.3.3 / 2020-09-09

- Fix missing dependencies in requirements.txt that were causing crashes.

# 0.3.2 / 2020-05-18

- fix: pathofexile.com/trade stability

# 0.3.1 / 2020-05-01

- fix: bug with item lists to crash at start

# 0.3.0 / 2020-05-01

- Added backend pooling: Query all backends for data in parallel

  - faster
  - no configuration hassle
  - easily extendable via other backends

# 0.2.0 / 2020-03-03

- Add customisable user configuration (see [here](README.md#configuration) for more details)

  - Limiting trade volume of first transaction based on user settings and stack sizes
  - Customisable stock requirements to filter certain traders
  - Customisable instead of pre-defined trading paths

- Quality of Life

  - CLI: Filter interfering trades
  - Increase offer limit for [https://pathofexile.com/trading](https://pathofexile.com/trading)
  - Filter offers with large outliers (>95th percentile)

# 0.1.1 / 2020-01-28

- Rewrote loading and creating item databases

  - Now reads items for both backends and merges them into a unified structure
  - Can now detect if a given item is supported by a respective backend
  - `PathFinder` now gives feedback when encountering an unsupported item, eg. from `pair_filter.json`

# 0.1.0 / 2020-01-12

- Massively improve speed by using [pathofexile.com/trade](https://pathofexile.com/trade) instead of [poe.trade](http://poe.trade)
