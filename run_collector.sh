PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Delirium" --path "data_analysis/raw/Delirium/Hardcore" --nofilter --fullbulk
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Delirium" --path "data_analysis/raw/Delirium/Softcore" --nofilter --fullbulk
