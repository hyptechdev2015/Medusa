#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Guessit customization."""
from __future__ import unicode_literals

from guessit.api import default_api

from medusa.name_parser.rules.properties import (
    blacklist,
    container,
    source_,
    other,
    screen_size
)
from medusa.name_parser.rules.rules import rules


default_api.rebulk.rebulk(blacklist())
default_api.rebulk.rebulk(source_())
default_api.rebulk.rebulk(screen_size())
default_api.rebulk.rebulk(other())
default_api.rebulk.rebulk(container())
default_api.rebulk.rebulk(rules())
