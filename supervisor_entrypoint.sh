#!/usr/bin/env bash

source /home/fredericokremer/miniconda3/bin/activate

eval "$(/home/fredericokremer/miniconda3/bin/./conda shell.bash hook)"

conda activate
conda activate bambu-enterprise-systematic-review

directory=$(dirname $(readlink -f $0))
cd $directory

make all_locally