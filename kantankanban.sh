#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Change this to the correct path of your Python main module
PYTHON_MODULE="task_manager"

# Run the Python module
python -m $PYTHON_MODULE "$@"
