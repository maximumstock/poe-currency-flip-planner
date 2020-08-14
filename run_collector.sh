export PYTHONPATH=$(pwd)
poetry run python data_analysis/collector.py --league "Hardcore Harvest" --path "data_analysis/raw/Harvest/Hardcore" --nofilter
sleep 10s
poetry run python data_analysis/collector.py --league "Harvest" --path "data_analysis/raw/Harvest/Softcore" --nofilter
