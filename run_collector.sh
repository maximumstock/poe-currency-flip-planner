PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Harvest" --path "data_analysis/raw/Harvest/Hardcore" --nofilter
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Harvest" --path "data_analysis/raw/Harvest/Softcore" --nofilter
