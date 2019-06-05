PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Legion" --path "data_analysis/raw/hc_legion_poetrade" --nofilter --fullbulk
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Legion" --path "data_analysis/raw/legion_poetrade" --nofilter --fullbulk
