#!/bin/sh
source .venv/bin/activate
python get_stokes.py $1
deactivate