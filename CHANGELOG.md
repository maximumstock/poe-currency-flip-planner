# Changelog

## v0.1.1 - 2020-01-28
- Rewrote loading and creating item databases
  - Now reads items for both backends and merges them into a unified structure
  - Can now detect if a given item is supported by a respective backend
  - `PathFinder` now gives feedback when encountering an unsupported item, eg. from `pair_filter.json`

## v0.1.0 - 2020-01-12
- Massively improve speed by using [pathofexile.com/trade](https://pathofexile.com/trade) instead of [poe.trade](http://poe.trade)

## 2019-05-05
* Fix rounding bug that creates insane arbitrage situations
