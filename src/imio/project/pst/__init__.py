# -*- coding: utf-8 -*-
"""Init and utils."""

import os

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('imio.project.pst')

PRODUCT_DIR = os.path.dirname(__file__)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


def add_path(path):
    path = path.strip('/ ')
    return "%s/%s" % (PRODUCT_DIR, path)
