#!/bin/bash -eu

if [ -z ${VIRTUAL_ENV+x} ]; then
    source venv/bin/activate
fi

python -mkusto_monitoring.main
