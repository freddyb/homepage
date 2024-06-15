#!/bin/sh
export LANG=en_US.UTF-8
source venv/bin/activate

#make html
make publish

echo
echo Rsync
rsync  -r output/* fbcom@kushida.uberspace.de:web/frederikbraun.de/
