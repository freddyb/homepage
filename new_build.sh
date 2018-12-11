#!/bin/sh
export LANG=en_US.UTF-8
source venv/bin/activate

make html
make publish

scp -r output/* freddyb@dubhe.uberspace.de:web/frederik-braun.com/
