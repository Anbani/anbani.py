from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='anbani',
    version='3.0.0',
    author="George Gach",
    author_email="georgegach@outlook.com",
    description="Georgian alphabet and language utilities for Natural Language Processing, script conversion and more.",
    license='GPL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anbani/anbani.py",
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "anbani = anbani.cli:main",
        ],
    },
    install_requires=[
        "hjson",
    ],
    extras_require={
        "pdf": ["pymupdf"],          # ebook2text / PDF extraction
        "dev": ["pytest", "pytest-cov"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
