#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://inventwithpython.com/blog/2014/12/20/translate-your-python-3-program-with-the-gettext-module/

import os
import gettext

# set the path where to find the locate files
localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
languages = {}
# set the available translations - actual hardcoded, but easily to be changed to a search routine
languages['de'] = gettext.translation(
	'zuul-ac', localedir, languages=['de'], fallback=True)
# _ = translate.gettext
# gettext.install('zuul-ac',localedir)

# use a user specific translation instead of a normal global translation


def gettext(text, language='en'):
	if not language or not language in languages:
		return text
	return languages[language].gettext(text)
