PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Hardcore Synthesis" --path "data_analysis/raw/hc_synthesis_poetrade" --nofilter --fullbulk
sleep 10s
PYTHONPATH=$(pwd) python3 data_analysis/collector.py --league "Synthesis" --path "data_analysis/raw/synthesis_poetrade" --nofilter --fullbulk
