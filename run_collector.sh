PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Delve" --path "data_analysis/raw/hc_delve"
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Delve" --path "data_analysis/raw/delve"
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Standard" --path "data_analysis/raw/standard"
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore" --path "data_analysis/raw/hardcore"
