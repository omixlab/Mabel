#!/usr/bin/env bash

source /opt/conda/bin/activate >> ~/.bashrc
eval "$(/opt/conda/bin/./conda shell.bash hook)"
conda activate bambu-enterprise-systematic-review
cd ..
source .env

celery -A src.utils.extractor.celery worker