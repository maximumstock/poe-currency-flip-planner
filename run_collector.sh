PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Blight" --path "data_analysis/raw/hardcore_blight" --nofilter --fullbulk
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Blight" --path "data_analysis/raw/blight" --nofilter --fullbulk
