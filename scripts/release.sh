#!/bin/bash

python setup.py sdist bdist_wheel
twine upload dist/*
rm -rf dist build anbani.egg-info