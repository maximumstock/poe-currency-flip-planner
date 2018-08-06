import argparse
import itertools
from src.pathfinder import PathFinder
from src.constants import currencies
from src.backends import poeofficial


def log_conversions(conversions):
  for c in conversions:
    log_conversion(c)

def log_conversion(c):
  print("{} {} -> {} {}: {} {}".format(c['starting'], c['from'], c['ending'], c['to'], c['winnings'], c['to']))
  for t in c['transactions']:
    print("\t@{} Hi, I'd like to buy your {} {} for {} {}. ({})".format(t['contact_ign'], t['received'], t['to'], t['paid'], t['from'], t['conversion_rate']))
  print("\n")

parser = argparse.ArgumentParser(description="CLI interface for PathFinder")
parser.add_argument("--league", default="Incursion", help="League specifier, ie. 'Incursion', 'Hardcore Incursion' or 'Flashback Event (BRE001)'")
parser.add_argument("--currency", default="all", help="Currency to flip")
parser.add_argument("--limit", default=3, help="Limit the number of displayed conversions")
arguments = parser.parse_args()

chosen_currencies = dict(itertools.islice(currencies.items(), 0, 10))
p = PathFinder(arguments.league, chosen_currencies, poeofficial)
p.run(3, False)
log_conversions(p.results[arguments.currency][:arguments.limit])
