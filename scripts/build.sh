#!/bin/bash

rm -rf dist build anbani.egg-info 
pip uninstall anbani -y
python setup.py sdist bdist_wheel
pip install --find-links=dist anbani --no-index
rm -rf build anbani.egg-info 