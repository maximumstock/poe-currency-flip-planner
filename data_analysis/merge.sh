#!/bin/sh

LEAGUES=(Betrayal Blight Delve Harvest Incursion Legion Synthesis)

for LEAGUE in ${LEAGUES[@]}
do
  python ./data_analysis/converter.py --path ./data_analysis/raw/$LEAGUE/Softcore
  mv ./data_analysis/raw/$LEAGUE/Softcore/merge.json ./data_analysis/merged/${LEAGUE}_softcore.json
  python ./data_analysis/converter.py --path ./data_analysis/raw/$LEAGUE/Hardcore
  mv ./data_analysis/raw/$LEAGUE/Hardcore/merge.json ./data_analysis/merged/${LEAGUE}_hardcore.json
done
