#!/bin/bash -eu

if [ -z ${VIRTUAL_ENV+x} ]; then
    source venv/bin/activate
fi

PIDFILE=.pid

cleanup() {
  kill -TERM $(cat $PIDFILE) >/dev/null 2>&1
  rm -f $PIDFILE
}

trap cleanup EXIT

python -mkusto_monitoring.main &
echo $! > $PIDFILE
wait
