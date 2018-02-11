# poe-currency-flip-planner

This tool is an attempt at planning short-term arbitrage deals of currency in Path of Exile.

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

* You have the same amount than before
* You have less than before
* You have more than before

Comparing different paths up to an arbitrary depth results in an answer to the question
in which succession currencies have to be traded to yield different profits/losses.

## Possible problems

* Exchange rates might not be online for long enough to complete complex transaction chains
* The supply/demand of both parties limits the number of paths that can be taken throughout
  the graph without collecting excess currency or investing additional currency to make
  up for the difference in trading volume between the parties.

  The simplest model assumes that at each step in the conversion chain the user is able
  to convert all currency that was acquired in the previous step

## Installation

`pip install -r requirements.txt`


## Running

`PYTHONPATH=$(pwd) python src/main.py` starts an example script that prints out all
profitable trade sequences from currency `x` back to currency `x`, given a list of
tradeable currencies.


## Tests

`PYTHONPATH=$(pwd) py.test tests/**`
