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
def categories_index(obj):
    # don't index project spaces (config value)
    if not IProjectSpace.providedBy(obj) and base_hasattr(obj, 'categories') and obj.categories:
        return obj.categories

    return common_marker


@indexer(IContentish)
def priority_index(obj):
    # don't index project spaces (config value)
    if not IProjectSpace.providedBy(obj) and base_hasattr(obj, 'priority') and obj.priority:
        return obj.priority

    return common_marker


@indexer(IContentish)
def representative_responsible_index(obj):
    if base_hasattr(obj, 'representative_responsible') and obj.representative_responsible:
        return obj.representative_responsible

    return common_marker


@indexer(IContentish)
def administrative_responsible_index(obj):
    if base_hasattr(obj, 'administrative_responsible') and obj.administrative_responsible:
        return obj.administrative_responsible

    return common_marker


@indexer(IContentish)
def manager_index(obj):
    if base_hasattr(obj, 'manager') and obj.manager:
        return obj.manager

    return common_marker


@indexer(IContentish)
def health_indicator_index(obj):
    if base_hasattr(obj, 'health_indicator') and obj.health_indicator:
        return obj.health_indicator

    return common_marker


@indexer(IContentish)
def progress_index(obj):
    if base_hasattr(obj, 'progress') and obj.progress:
        return obj.progress

    return '0'


@indexer(IContentish)
def extra_concerned_people_index(obj):
    if base_hasattr(obj, 'extra_concerned_people') and obj.extra_concerned_people:
        return obj.extra_concerned_people

    return common_marker
