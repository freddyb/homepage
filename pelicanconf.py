#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Frederik'
SITENAME = u"Frederik Braun"

RELATIVE_URLS = True ## for testing, shouldnt point to actual domain


# Feed generation: generate "all in one" feed, but omit feeds per category,tag,author
FEED_ALL_ATOM = 'feeds/all.atom.xml'
FEED_ALL_RSS = 'feeds/all.rss.xml'
CATEGORY_FEED_ATOM = None
CATEGORY_FEED_RSS = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
TAG_FEED_ATOM = None
TAG_FEED_RSS = None
CATEGORY_FEED_ATOM = None
CATEGORY_FEED_RSS = None
TRANSLATION_FEED_ATOM = None
TRANSLATION_FEED_RSS = None

TIMEZONE = 'Europe/Paris'
DEFAULT_LANG = u'en_US'
LOCALE = 'en_US'

# Blogroll
LINKS = ()


# images not used, but in here by default, so why not *shrugs*
STATIC_PATHS = ['images', 'publications', 'publications/thesis', 'js']

# Main Menu
#MENUITEMS = (("Blog", SITEURL), ("About", SITEURL + "/about"))

# Social widget
#SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

THEME = "/home/freddy/src/homepage/fb-mnmlist"

#PIWIK_URL = "piwik-qxawkjrxp.rhcloud.com"
#PIWIK_SITE_ID = 1
