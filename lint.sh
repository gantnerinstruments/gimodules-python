#!/bin/bash
echo "Running black (code formatting)..."
black "$1"
echo "Running flake8 (pep8)..."
flake8 "$1"
echo "Running mypy (type hints)..."
mypy "$1"
