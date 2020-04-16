#!/bin/sh
export LANG=en_US.UTF-8
source venv/bin/activate

make html
make publish

rsync -v -r output/* fbcom@kushida.uberspace.de:web/frederik-braun.com/
