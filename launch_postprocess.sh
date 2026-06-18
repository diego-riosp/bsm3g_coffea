#!/bin/bash

python3 run_postprocess.py -w qcd_tf_ele_SingleMu_weightedv2 -y 2016preVFP --postprocess --plot --log --eos
python3 run_postprocess.py -w qcd_tf_ele_SingleMu_weightedv2 -y 2016postVFP --postprocess --plot --log --eos
python3 run_postprocess.py -w qcd_tf_ele_SingleMu_weightedv2 -y 2017 --postprocess --plot --log --eos
python3 run_postprocess.py -w qcd_tf_ele_SingleMu_weightedv2 -y 2018 --postprocess --plot --log --eos
