import logging
from src.commons import unique_conversions_by_trader_name

from src.pathfinder import PathFinder


def log_conversions(conversions, limit):
    for c in conversions[:limit]:
        log_conversion(c)


def log_conversion(c):
    logging.info("\t{} {} -> {} {}: {} {}".format(c["starting"], c["from"],
                                                  c["ending"], c["to"],
                                                  c["winnings"], c["to"]))
    for t in c["transactions"]:
        logging.info(
            "\t\t@{} Hi, I'd like to buy your {} {} for {} {} in {}. ({}x)".
            format(
                t.contact_ign,
                t.received,
                t.want,
                t.paid,
                t.have,
                t.league,
                t.conversion_rate,
            ))
    logging.info("\n")


def execute_pathfinding(currency: str, league: str, limit: int, item_pairs,
                        user_config, excluded_traders):
    p = PathFinder(league, item_pairs, user_config, excluded_traders)
    p.run(2)

    try:
        logging.info("\n")
        if currency == "all":
            for c in p.graph.keys():
                conversions = unique_conversions_by_trader_name(p.results[c])
                log_conversions(conversions, limit)
        else:
            conversions = unique_conversions_by_trader_name(
                p.results[currency])
            log_conversions(conversions, limit)

    except KeyError:
        logging.warning(
            "Could not find any profitable conversions for {} in {}".format(
                currency, league))
