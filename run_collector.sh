PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Betrayal" --path "data_analysis/raw/hc_betrayal" --poetrade
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Betrayal" --path "data_analysis/raw/betrayal" --poetrade
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Standard" --path "data_analysis/raw/standard" --poetrade
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore" --path "data_analysis/raw/hardcore" --poetrade
