#!/bin/bash

python3 run_postprocess.py -w 1b1e -y 2016preVFP --postprocess --plot --log --eos
python3 run_postprocess.py -w 1b1e -y 2016postVFP --postprocess --plot --log --eos
python3 run_postprocess.py -w 1b1e -y 2017 --postprocess --plot --log --eos
python3 run_postprocess.py -w 1b1e -y 2018 --postprocess --plot --log --eos
