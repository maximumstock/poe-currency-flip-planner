PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Metamorph" --path "data_analysis/raw/Metamorph/Hardcore" --nofilter --fullbulk
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Metamorph" --path "data_analysis/raw/Metamorph/Softcore" --nofilter --fullbulk
