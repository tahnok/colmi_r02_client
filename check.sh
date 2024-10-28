#!/bin/bash

set -ex

ruff format

ruff check --fix

mypy colmi_r02_client

pytest

poetry check --lock
