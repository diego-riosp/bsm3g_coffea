#!/bin/bash -xe

WORKFLOW=$1
YEAR=$2
BASEDIR=$3
X509PATH=$4

export XRD_NETWORKSTACK=IPv4
export XRD_RUNFORKHANDLER=1
export X509_USER_PROXY=$X509PATH

cd $BASEDIR
python3 run_postprocess.py -w "$WORKFLOW" -y "$YEAR" --postprocess --eos --log --plot
