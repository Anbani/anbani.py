# Controlled environment for testing anbani.py.
#
#   docker build -t anbani-py .
#   docker run --rm anbani-py              # run the test suite (pytest)
#
# Python 3.12 is the top of the CI matrix (3.10/3.11/3.12). Installs the package
# with its dev extras (pytest, pytest-cov) plus the sole runtime dep (hjson).
FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -e ".[dev]"

CMD ["pytest", "-q"]
