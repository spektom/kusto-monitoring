#!/bin/bash -eu

PIDFILE=.pid
kill -1 $(cat $PIDFILE) >/dev/null 2>&1
