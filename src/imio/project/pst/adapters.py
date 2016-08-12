# -*- coding: utf-8 -*-
from datetime import date
from DateTime import DateTime

from plone import api
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.utils import base_hasattr
from Products.PluginIndexes.common.UnIndex import _marker as common_marker

from collective.contact.plonegroup.utils import organizations_with_suffixes

from imio.project.core.content.projectspace import IProjectSpace


UNSET_DATE_VALUE = date(3900, 1, 1)  # value used to mark the fact that a date is not set, we need a date in the future for beginning-is-late collection


class UserIsAdministrativeResponsibleCriterion(object):

    def __init__(self, context):
        self.context = context

    @property
    def query(self):
        groups = api.group.get_groups(user=api.user.get_current())
        orgs = []
        orgs = organizations_with_suffixes(
            groups, ['administrative_responsible'])

        # if orgs is empty list, nothing is returned => ok
        return {'administrative_responsible': {'query': orgs}}


class UserIsActionEditorCriterion(object):

    def __init__(self, context):
        self.context = context

    @property
    def query(self):
        groups = api.group.get_groups(user=api.user.get_current())
        orgs = []
        orgs = organizations_with_suffixes(
            groups, ['actioneditor'])

        # if orgs is empty list, nothing is returned => ok
        return {'manager': {'query': orgs}}


class TaskInAssignedGroupCriterion(object):

    """Return catalog criteria following assigned group member."""

    def __init__(self, context):
        self.context = context

    @property
    def query(self):
        groups = api.group.get_groups(user=api.user.get_current())
        orgs = organizations_with_suffixes(
            groups, ['validateur', 'editeur', 'lecteur'])
        # if orgs is empty list, nothing is returned => ok
        return {'assigned_group': {'query': orgs}}


class ChildrenActionDeadlineHasPassedCriterion(object):

    def __init__(self, context):
        self.context = context

    @property
    def query(self):
        collection_query = {
        'planned_end_date': {'query': DateTime(), 'range': 'max'},
        'portal_type': {'query': ['pstaction']}, 'sort_on': 'created', 'sort_order': 'descending'}
        # from plone.app.querystring import queryparser
        # collection_query = queryparser.parseFormquery(collection, collection.query)
        return {
            ':has_child': {'query': collection_query}}

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


@indexer(IContentish)
def effective_begin_date_index(obj):
    if base_hasattr(obj, 'effective_begin_date') and obj.effective_begin_date:
        return obj.effective_begin_date

    return UNSET_DATE_VALUE
