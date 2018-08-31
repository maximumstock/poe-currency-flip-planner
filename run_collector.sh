PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Delve" --path "data_analysis/raw/hc_delve"
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Delve" --path "data_analysis/raw/delve"
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Standard" --path "data_analysis/raw/standard"
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore" --path "data_analysis/raw/hardcore"
