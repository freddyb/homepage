#!/bin/sh
export LANG=en_US.UTF-8
source venv/bin/activate

#make html
make publish

echo
echo Rsync
rsync --info=progress2 -r output/* fbcom@kushida.uberspace.de:web/frederik-braun.com/
