#!/usr/bin/env bash
export LANG=en_US.UTF-8
source venv/bin/activate

rm -r output-staging/*
pelican content/ -o output-staging/ -s stagingconf.py 
rsync -v -r output-staging/ fbcom@kushida.uberspace.de:/var/www/virtual/fbcom/http09.on.web.security.plumbing/
