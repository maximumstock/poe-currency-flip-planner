export PYTHONPATH=$(pwd)
poetry run python data_analysis/collector.py --league "Hardcore Heist" --path "data_analysis/raw/Heist/Hardcore" --nofilter
sleep 10s
poetry run python data_analysis/collector.py --league "Heist" --path "data_analysis/raw/Heist/Softcore" --nofilter
