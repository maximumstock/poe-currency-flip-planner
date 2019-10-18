# poe-currency-flip-planner

![](https://api.travis-ci.com/maximumstock/poe-currency-flip-planner.svg?branch=master)

This tool is an attempt at finding short-term arbitrage deals of currency and items in Path of Exile.

## Background

Via [poe.trade](http://currency.poe.trade) one can look for currently offered currency
conversion rates of other players. By indexing these conversion rates, it should be
possible to find a perfect chain of conversions between two preselected currencies that
yields the most arbitrage value at that point in time.

This data can be modeled as a graph where the currently available conversion rates are
single edges between nodes (currencies). Basically, this is the kind of data trade websites
such as [poe.trade](http://currency.poe.trade) show already.

Given a currency, circular paths of arbitrary length can be found within that graph that
describe different ways to trade the currency for different currencies `x` times until
trading back for the starting currency. Each of these paths yields one of the following
outcomes:

- You have the same amount as before
- You have less than before
- You have more than before

Comparing different paths up to an arbitrary depth results in an answer to the question
in which succession currencies have to be traded to yield different profits/losses.

## How to use

If you simply want to use this tool to find profitable trades,
please use `python cli.py` as a CLI interface.
See `src/cli.py` or `python cli.py --help` for help and options.
This uses poe.trade per default as it is faster than the official Path of Exile Trading API.

After a while you will get a bunch of text printed out with your suggested conversions.

### Default Settings

Per default, we use all traditional currency items (aka `Orbs` plus some manually selected)
for this search.
Additionally, we use a data-mined filter (see `data_analysis/README.md`) to only
request data for pairs that usually provide profitable conversions.
You might manually alter this filter by editing `assets/pair_filter.json`.

### Options

There are the following options:

1. look at all items poe.trade supports (--nofilter + --fullbulk)
2. look at all traditional currencies, ie. `Orbs` (--nofilter)
3. look at a data-mined preset of item pairs that are probably profitable most of the time, see `assets/pair_filter.json`, the default

Please note that option #1 takes a long time and is basically useless unless
you want to collect your own data for analysis (see `data_analysis/README.md`).
However, you might just use `run_collector.sh` (which uses `data_analyis/collector.py`)
and is specifically built for this purpose.

If you are interested in a subset of this, eg. all Orbs + Fossils, you might edit
`assets/poetrade.json` to only contain those items and run option #1.
You can always reset `assets/poetrade.json` to its default by running `python src/asset_mgr.py`.
View this as an Path of Exile item filter :).

### Exclude Traders

Some traders offer either very good or bad conversion rates, depending on their
price-fixing goal.
As of now there is no built-in way to detect price-fixing offers.
If you want to exclude traders you can add their names to `excluded_traders.txt`
(one name per line).

### Library Usage

If you want to use this project as a library/dependency, feel free to use the
`PathFinder` class (see `src/pathfinder.py`) as an API.

The PathFinder class is simply a static interface for finding profitable trade
paths for arbitrage. You give it the league, a list of currencies and a backend
instance (eg. `backends/poeofficial.py`). For each
currency it starts looking for all profitable paths that start and end with that
currency, given a maximum transaction length (default: 3). All stages of data
(eg. list of collected offers via the respective trading backend, the constructed
graph of offers and the found profitable paths) are part of each PathFinder
instance and can simply be accessed and used for further work.

## How it works

- Currency trade offers are collected from a backend provider, eg.
  - [poe.trade](http://poe.trade)
  - [Path of Exile Trade](https://www.pathofexile.com/trade/exchange)
- I currently use [poe.trade](http://currency.poe.trade) as a
  default, since they seem to automatically filter out certain price-fixing offers, which
  is really great!
- Found trade offers are used to build a fully connected graph with currencies as nodes
  and one edge for each offer of each pair of non-identical currencies.
- The offered exchange rates and stocks are used to find the most profitable trading paths
  within the graph.

At the end, it might look something like this:

![](examples/result_screenshot.png)

## Problems

- Exchange rates might not be online for long enough to complete complex transaction chains
- The supply/demand of both parties limits the number of paths that can be taken throughout
  the graph without collecting excess currency or investing additional currency to make
  up for the difference in trading volume between the parties.

  The simplest model assumes that at each step in the conversion chain the user is able
  to convert all currency that was acquired in the previous step

## Installation

I highly recommend using [Pipenv](https://github.com/pypa/pipenv) for managing
Python projects and their dependencies.

1. `pipenv shell` to enter a shell session with my environment settings
2. `pipenv install` to install all dependencies

I use Python >=3.7 for everything. I haven't tried running it with different versions.

## Tests

I wrote a few simple unit tests to make the data fetching and parsing, graph
construction and traversal and path evaluation a bit more robust. You can run
those tests using predefined data structures via `python -m pytest tests`.

## Data Exploration

The data that is used for the analysis is not part of this repository. Please
collect your own data. You can use `run_collector.sh` for this. It starts a
`PathFinder` instance (see `src/pathfinder.py`) for each league. I like running
this as a cronjob every 30 minutes. The collected PathFinder instances are then
pickled and persisted in their respective folders, specified in `run_collector.sh`.

See [here](data_analysis/README.md) for discussion.

### General Workflow (as of now)

1. Collect Data
   `python data_analysis/collector.py --league "Blight" --path "data_analysis/Blight/Softcore"`
2. Merge single `.pickle` files into one `merge.pickle`
   `python data_analysis/converter.py --path "data_analysis/raw/Delve/Softcore"`
3. Run analysis.py
   `python data_analysis/analysis.py --path "data_analysis/raw/Delve/Softcore/merge.pickle"`

## Ideas & Roadmap

See [todo.org](todo.org) (beware of org-mode format from Emacs :)) for ideas, future features, etc. Feel free to send
me any feedback, either via email or PR.
