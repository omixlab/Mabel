#!/usr/bin/env bash

source /opt/conda/bin/activate >> ~/.bashrc
eval "$(/opt/conda/bin/./conda shell.bash hook)"
conda activate bambu-enterprise-systematic-review

export FLASK_APP=__init__.py
cd ..

source .env

FLASK_APP=src/__init__.py
flask run --host=0.0.0.0 --port=5000