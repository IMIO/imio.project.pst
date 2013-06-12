# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer


class IImioProjectPSTLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer."""


class IListContainedDexterityObjectsForDisplay(Interface):
    """Adapter interface that returns the dexterity objects contained
       in a dexterity Container in a state to be displayed."""
