# claon-admin-server
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-31010/)
[![CI](https://github.com/Co-Laon/claon-admin-server/actions/workflows/ci.yml/badge.svg)](https://github.com/Co-Laon/claon-admin-server/actions/workflows/ci.yml)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![codecov](https://codecov.io/gh/Co-Laon/claon-admin-server/branch/develop/graph/badge.svg?token=it2dGzqx3z)](https://codecov.io/gh/Co-Laon/claon-admin-server)


## Installation

upload image to docker for local environment
```bash
docker-compose -f docker-compose.yml up -d
```

install dependencies of this project
```bash
python3 -m pip install --upgrade pip
pip3 install poetry==1.4.0
poetry install
```

## Run

### local
```bash
poetry run task local
```

### prod
```bash
poetry run task prod
```

### test
```bash
poetry run task test
```

## Run Celery

### local
```bash
poetry run task celeryLocal
```

### prod
```bash
poetry run task celeryProd 
```