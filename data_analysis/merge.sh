#!/bin/sh

LEAGUES=(Betrayal Blight Delirium Delve Harvest Incursion Legion Synthesis)

for LEAGUE in ${LEAGUES[@]}
do
  python ./converter.py --path ./raw/$LEAGUE/Softcore
  mv ./raw/$LEAGUE/Softcore/merge.pickle ./merged/${LEAGUE}_softcore.pickle
  python ./converter.py --path ./raw/$LEAGUE/Hardcore
  mv ./raw/$LEAGUE/Hardcore/merge.pickle ./merged/${LEAGUE}_hardcore.pickle
done
