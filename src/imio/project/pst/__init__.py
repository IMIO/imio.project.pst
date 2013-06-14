# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('imio.project.pst')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    from imio.project.pst import monkey
    monkey.__name__  # make pyflakes happy...
