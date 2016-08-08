# -*- coding: utf-8 -*-
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.utils import base_hasattr
from Products.PluginIndexes.common.UnIndex import _marker as common_marker

from imio.project.core.content.projectspace import IProjectSpace


####################
# Indexes adapters #
####################

@indexer(IContentish)
def priority_index(obj):
    # don't index project spaces (config value)
    if not IProjectSpace.providedBy(obj) and base_hasattr(obj, 'priority') and obj.priority:
        return obj.priority

    return common_marker
