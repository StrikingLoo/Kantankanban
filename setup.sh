#!/bin/bash

export KTKB_PATH=$(pwd)
python -m venv ./venv
source venv/bin/activate
python -m pip install -r requirements.txt
