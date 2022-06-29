from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='anbani',
    version='0.9.1',
    author="George Gach",
    author_email="georgegach@outlook.com",
    description="Georgian alphabet and language utilities for Natural Language Processing, script conversion  and more.",
    license='GPL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anbani/anbani.py",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "pymupdf",
        "hjson",
        "numpy",
        "pandas",
        "tqdm",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
