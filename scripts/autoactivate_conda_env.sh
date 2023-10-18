#!/usr/bin/bash

echo source /opt/conda/bin/activate >> ~/.bashrc
echo eval "$(/opt/conda/bin/./conda shell.bash hook)" >> ~/.bashrc
echo "conda activate bambu-enterprise-systematic-review" >> ~/.bashrc