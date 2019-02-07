# Data Exploration

***Note: WIP!!!***

Everything I present in this section is very experimental and might be completely wrong. This is just something I enjoy personally without any formal affiliation to the topic of data science, so be nice and don't take anything too seriously.

With a working trade crawler we can now collect currency trading data and try to gain some insights from it. In this section I'll try to document what I've tried to achieve this.

## Setup
I have collected currency trading information via this tool for a fixed set of currencies, about every thirty minutes during the time the Delve leagues were active.
This leaves me with regular snapshots for the time between `2018-09-02` until `2018-10-19` for the leagues `Delve`, `Hardcore Delve`, `Standard` and `Hardcore`.

The set of currencies was more or less consciously chosen. There are a lot of common and niche currencies I have not included, but the list for this test run was:

<img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/c/cb/Orb_of_Augmentation_inventory_icon.png?version=c658d2f16f22512f9e524c1b2ad58788" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/6/67/Orb_of_Transmutation_inventory_icon.png?version=2f95dd6abd2e9e6eb5a5098350f444b9" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/f/fd/Chromatic_Orb_inventory_icon.png?version=143829f3bc33b5cd2727d057a330202b" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/5/51/Orb_of_Scouring_inventory_icon.png?version=2490d92836e555d1fa9ce8b96a4cde98" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/9/9c/Chaos_Orb_inventory_icon.png?version=3a4a05170a16dad38a3f29c18587e872" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/d/d8/Orb_of_Alteration_inventory_icon.png?version=cf6e20cf8835884b69ca50a56bc076de" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/5/55/Cartographer%27s_Chisel_inventory_icon.png?version=0c4cfe265e9b3bc8bc831dd60674f858" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/e/e2/Gemcutter%27s_Prism_inventory_icon.png?version=1bce839e57a840244de6e9d07b929624" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/6/62/Orb_of_Fusing_inventory_icon.png?version=442fbda832963ee3a42207bef33637a0" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/3/33/Regal_Orb_inventory_icon.png?version=20f63c824d34f861178e0f23d13bbd14" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/9/9f/Orb_of_Alchemy_inventory_icon.png?version=6a3df396aa93c31adceb0f9afe117541" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/2/26/Exalted_Orb_inventory_icon.png?version=010520296d3532afddbb609b1a4fe45b" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/a/a8/Orb_of_Regret_inventory_icon.png?version=08bf23a9c60c5afc34bda1786ed369bd" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/4/49/Jeweller%27s_Orb_inventory_icon.png?version=1a955998de8bce79f034434e273ed611" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/5/58/Divine_Orb_inventory_icon.png?version=1cb4cef4c16efed714eb1a01977ed5c3" width="32"/><img src="https://d1u5p3l4wpay3k.cloudfront.net/pathofexile_gamepedia/2/2c/Vaal_Orb_inventory_icon.png" width="32"/>

For each 2-permutation of currencies from the list above, I request trade offers from [poe.com/trade](http://pathofexile.com/trade). For each list of offers, I filter out those who do not come with stock information, because this piece of information is important for constructing profitable trading paths, and then select the first five offers from these.

For the list of 17 currencies above this makes 272 permutations, 5 offers each, resulting in 1360 offers at max. At this point I'd like to introduce `transaction` as a synonym for an offer on [poe.com/trade](http://pathofexile.com/trade).

From this list of transactions, I construct a fully-meshed graph. For each currency from the above list, I start a breadth-first search to find all profitable trading paths (with a maximum length of 3 transactions) starting **AND** ending in that currency. So at the end of this I have 17 lists of profitable trading paths along this transaction graph. I call these trading paths `conversions`.

At this point I'd like to clarify that my definition of a conversion being **profitable** means that you have more of the respective currency after serially undertaking every transaction of the conversion. This means that the profitability of a conversion can solely rely on one of many transaction in the conversion. This is important to keep in mind for the heatmap visualization below.

## Importance of certain currencies for profitable conversions
So this should be the most interesting bit of data for now. Below you can see how often each 2-permutation transaction was found in a profitable conversion.
Each number is calculated as the `total number of profitable conversions for that transaction over all snapshots` divided by `number of snapshots`.
The higher the number, the more profitable conversions were dependent on transactions between those two currencies.
Below are heatmap visualizations for each league during the Delve season.

### Delve
![](results/delve/delve.png)

### Hardcore Delve
![](results/delve/hardcore_delve.png)

### Standard
![](results/delve/standard.png)

### Hardcore
![](results/delve/hardcore.png)

So we can see that selling `Chaos Orbs` for `Vaal Orbs` in `Delve` was especially often part of profitable conversions, averaging around 65 profitable conversions per snapshot. Keep in mind that this only means that there was a least one offer from `Chaos Orbs` to `Vaal Orbs` which ended up in a lot of conversions, which in turn ended up being profitable. It does not necessarily mean that there were a lot of offers from `Chaos Orbs` to `Vaal Orbs`.

As stated above, the maximum length of trading paths I evaluated was `3`, meaning three trades in a row, ending up at the starting currency, ie. trading `Exalted` -> `Regrets` -> `Chaos` -> `Exalted`. If the middle transaction is particularly profitable, the other two might be bad or average at best, but are improved by the middle one. At the same time, it does not mean that a certain transaction/2-permuation is especially profitable, but rather leads to a currency that itself offers more profitable transactions along the way.

We can also see that the matrix is relatively sparse, meaning only relatively few 2-permutations are often seen in profitable conversions. For example, all 2-permutations including `Orbs of Augmentation` or `Orbs of Transmutation` are basically non-existent when it comes to my method for finding profitable conversions.

Generally speaking, selling and buying `Chaos Orbs` looks like the easiest way of making profitable currency trades. This of course makes sense considering the significance of `Chaos Orbs` in everyday trades.
