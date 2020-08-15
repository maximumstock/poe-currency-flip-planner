import numpy as np
import pickle
from matplotlib import pyplot as plt
import itertools
import argparse
import operator
from src.trading import ItemList

item_list = ItemList.load_from_file()
all_items = [x for x in item_list.items.keys()]
all_currencies = [
    x.name for x in item_list.items.values()
    if x.is_basic_currency and x.is_currency
]
"""
Helpers
"""


def extract_transaction_edges(day):
    """
    Extracts a list of transactions from all conversions for all currencies
    from the `results` property of a PathFinder instance.
    """
    transaction_edges = []

    for currency in day["results"]:
        for conversion in day["results"][currency]:
            for transaction in conversion["transactions"]:
                transaction_edges.append(transaction)

    return transaction_edges


"""
Plotting stuff
"""


def stuff_per_day(data, timestamps):
    """
    How many things per measured instance, eg.
    * Total number of offers
    * Total number of profitable conversions across all currencies
    """
    def sum_results(results):
        s = 0
        for k in results.keys():
            s = s + len(results[k])
        return s

    number_of_results = [sum_results(x["results"]) for x in data]
    # number_of_offers = [len(x["offers"]) for x in data]

    plt.figure()
    plt.title("Total number of profitable conversions")
    plt.xlabel("Time")
    plt.plot(number_of_results, "b-", label="Number of profitable conversions")
    # plt.plot(number_of_offers, "r-", label="Number of offers")
    # plt.legend(["Number of transactions", "Number of offers"])
    plt.show()


def number_of_edges_between_currencies_per_instance(data, timestamps):
    """
    How many connections between each pair of currency were there per measured
    instance
    """

    assert len(data) == len(timestamps)

    daily_edges = []
    for i in range(len(data)):
        edges = extract_transaction_edges(data[i])
        daily = {
            "timestamp":
            timestamps[i],
            "transactions":
            edges,
            "sorted_transactions":
            sorted(edges, key=lambda x: "{}-{}".format(x["from"], x["to"])),
        }
        daily_edges.append(daily)

    # Collect all key occurences per timestamp to a separate list
    # NOTE: Lists are not all the same size, because of how groupby works,
    # so a daily value per key is a little bit harder to get and probably quite
    # meaningless, so we don't do it for now
    key_groups = {}
    for idx, day in enumerate(daily_edges):
        for key, group in itertools.groupby(
                day["sorted_transactions"],
                lambda x: "{}-{}".format(x["from"], x["to"])):
            if key not in key_groups:
                key_groups[key] = []
            key_groups[key].append(sum(1 for _ in group))

    # Sum each list up, indicating the total number of transactions for that
    # currency combination througout all measured instances
    for key in key_groups:
        key_groups[key] = np.sum(key_groups[key])

    # x = currencies
    # y = currencies
    z = []
    combos = itertools.product(all_currencies, repeat=2)
    for combo in combos:
        key = "{}-{}".format(combo[0], combo[1])
        if key in key_groups:
            z.append(key_groups[key] / len(timestamps))
        else:
            z.append(0)

    Z = np.array(z).reshape(len(all_currencies), len(all_currencies))
    return key_groups, Z


def plot_heatmap(x,
                 y,
                 z,
                 league,
                 start_date,
                 end_date,
                 x_label="Selling",
                 y_label="Buying"):
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(z, aspect="auto")
    ax.set_xticks(np.arange(len(x)))
    ax.set_yticks(np.arange(len(y)))
    ax.set_xticklabels(x)
    ax.set_yticklabels(y)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.setp(ax.get_xticklabels(),
             rotation=45,
             ha="right",
             rotation_mode="anchor")
    ax.set_title(
        "Average number of profitable conversions per edge and snapshot\n{} ({} - {})"
        .format(league, start_date, end_date))
    fig.tight_layout()
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Number of conversions", rotation=-90, va="bottom")
    for i in range(len(x)):
        for j in range(len(y)):
            ax.text(j,
                    i,
                    round(z[i, j], 1),
                    ha="center",
                    va="center",
                    color="w")
    return fig, ax


def find_relevant_currency_hops(data, minimum=0.25):
    timestamps = [x["timestamp"] for x in data]
    key_groups, _ = number_of_edges_between_currencies_per_instance(
        data, timestamps)
    k = filter(
        lambda x: True if x[1] / len(timestamps) > minimum else False,
        key_groups.items(),
    )
    m = map(lambda x: (x[0], x[1] / len(timestamps)), k)
    sorted_groups = sorted(m, key=operator.itemgetter(1))
    sorted_groups.reverse()

    return {"groups": sorted_groups, "share": len(sorted_groups) / len(data)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Analysis")
    parser.add_argument("--path", help="Path to conversion file to analyze.")
    arguments = parser.parse_args()

    file_path = arguments.path

    with open(file_path, "rb") as f:
        data = pickle.load(f)
    timestamps = [x["timestamp"] for x in data]
    s_timestamps = sorted(timestamps)
    min_timestamp = timestamps[0].split(" ")[0]
    max_timestamp = timestamps[-1].split(" ")[0]
    league = data[0]["league"]
    currencies = sorted(all_currencies)

    # stuff_per_day(data, timestamps)
    # # Heatmap
    _, heatmap_data = number_of_edges_between_currencies_per_instance(
        data, timestamps)
    fig, ax = plot_heatmap(all_currencies, all_currencies, heatmap_data,
                           league, min_timestamp, max_timestamp)
    plt.savefig("data_analysis/results/heatmap_{}_{}-{}".format(
        league, min_timestamp, max_timestamp))
    # Relevant currency hops
    # hops = find_relevant_currency_hops(data)
