#!/bin/bash -e

case $1 in
  "long")
    shift
    python app.py
    ;;
  "short")
    shift
    python app-short.py
    ;;
  *)
    echo "usage: $0 [long|short]"
    exit 1
    ;;
esac
