PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Betrayal" --path "data_analysis/raw/hc_betrayal_poetrade" --poetrade --nofilter --fullbulk
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Betrayal" --path "data_analysis/raw/betrayal_poetrade" --poetrade --nofilter --fullbulk
