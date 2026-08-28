#!/bin/bash

python3 run_postprocess.py -w ztomumu -y 2022preEE --postprocess --plot --log --eos
python3 run_postprocess.py -w ztomumu -y 2022postEE --postprocess --plot --log --eos
python3 run_postprocess.py -w ztomumu -y 2023preBPix --postprocess --plot --log --eos
python3 run_postprocess.py -w ztomumu -y 2023postBPix --postprocess --plot --log --eos
python3 run_postprocess.py -w ztoee -y 2022preEE --postprocess --plot --log --eos
python3 run_postprocess.py -w ztoee -y 2022postEE --postprocess --plot --log --eos
python3 run_postprocess.py -w ztoee -y 2023preBPix --postprocess --plot --log --eos
python3 run_postprocess.py -w ztoee -y 2023postBPix --postprocess --plot --log --eos
