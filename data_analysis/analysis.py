import numpy as np
import pickle
from matplotlib import pyplot as plt
import itertools

with open("data_analysis/conversion.pickle", "rb") as f:
  data = pickle.load(f)
timestamps = [x["created_at"] for x in data]


"""
Helpers
"""

"""
Extracts a list of transactions from all conversions for all currencies 
from the `results` property of a PathFinder instance.
"""
def extract_transaction_edges(day):
  transaction_edges = []

  for currency in day["results"]:
    for conversion in day["results"][currency]:
      for transaction in conversion["transactions"]:
        transaction_edges.append(transaction)

  return transaction_edges



"""
Plotting stuff
"""


"""
How many things per measured instance, eg.
  * Total number of offers
  * Total number of profitable conversions across all currencies
"""
def stuff_per_day(data, timestamps):
  def sum_results(results):
    s = 0
    for k in results.keys():
      s = s + len(results[k])
    return s

  number_of_results = [sum_results(x["results"]) for x in data]
  number_of_offers = [len(x["offers"]) for x in data]

  plt.figure()
  plt.title("Total number of transactions \nof all profitable conversions \nper 10 minutes (2018-05-14 - 2018-05-24)")
  plt.xlabel("Time (in 10 minute instances)")
  plt.plot(number_of_results, "b-", label="Number of transactions")
  plt.plot(number_of_offers, "r-", label="Number of offers")
  plt.legend(["Number of transactions", "Number of offers"])
  plt.show()



"""
How many connections between each pair of currency were there per measured
instance
"""
def number_of_edges_between_currencies_per_instance(data, timestamps):

  assert len(data) == len(timestamps)

  currencies = list(data[0]["currencies"].keys())

  daily_edges = []
  for i in range(len(data)):
    edges = extract_transaction_edges(data[i])
    daily = {
      "timestamp": timestamps[i],
      "transactions": edges,
      "sorted_transactions": sorted(edges, key=lambda x: "{}-{}".format(x["from"], x["to"]))
    }
    daily_edges.append(daily)


  # Collect all key occurences per timestamp to a separate list
  # NOTE: Lists are not all the same size, because of how groupby works,
  # so a daily value per key is a little bit harder to get and probably quite
  # meaningless, so we don't do it for now
  key_groups = {}
  for idx, day in enumerate(daily_edges):
    for key, group in itertools.groupby(day["sorted_transactions"], lambda x: "{}-{}".format(x["from"], x["to"])):
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
  for combo in itertools.product(currencies, repeat=2):
    key = "{}-{}".format(combo[0], combo[1])
    if key in key_groups:
      z.append(key_groups[key]/len(timestamps))
    else:
      z.append(0)

  Z = np.array(z).reshape(len(currencies), len(currencies))
  plot_heatmap(currencies, currencies, Z)

  

def plot_heatmap(x, y, z):
  fig, ax = plt.subplots()
  im = ax.imshow(z)
  # We want to show all ticks...
  ax.set_xticks(np.arange(len(x)))
  ax.set_yticks(np.arange(len(y)))
  # ... and label them with the respective list entries
  ax.set_xticklabels(x)
  ax.set_yticklabels(y)
  # Rotate the tick labels and set their alignment.
  plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
  ax.set_title("Average number of transactions \nbetween currencies from profitable conversions \nper 10 minutes (2018-05-14 - 2018-05-24)")
  fig.tight_layout()
  # Create colorbar
  cbar = ax.figure.colorbar(im, ax=ax)
  cbar.ax.set_ylabel("Number of Transactions", rotation=-90, va="bottom")
  # Loop over data dimensions and create text annotations.
  for i in range(len(x)):
    for j in range(len(y)):
      text = ax.text(j, i, round(z[i, j], 1), ha="center", va="center", color="w")
  plt.show()


stuff_per_day(data, timestamps)
number_of_edges_between_currencies_per_instance(data, timestamps)
