# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from Products.CMFCore.interfaces import ISiteRoot
from collective.contact.plonegroup.utils import organizations_with_suffixes
from datetime import date
from DateTime import DateTime
from collective.task.behaviors import ITask
from imio.project.pst import EMPTY_STRING
from imio.project.pst.content.action import IPSTAction
from imio.project.pst.content.action import IPSTSubAction
from plone import api
from plone.app.contentmenu.menu import ActionsSubMenuItem as OrigActionsSubMenuItem
from plone.app.contentmenu.menu import FactoriesSubMenuItem as OrigFactoriesSubMenuItem
from plone.app.contentmenu.menu import WorkflowMenu as OrigWorkflowMenu
from plone.indexer import indexer
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.utils import base_hasattr
from Products.PluginIndexes.common.UnIndex import _marker as common_marker

# value used to mark the fact that a date is not set, we need a date in the future for beginning-is-late collection
UNSET_DATE_VALUE = date(3900, 1, 1)


def validation_criterion(context, suffixes):
    """ Return a query criterion corresponding to current user validation level """
    groups = api.group.get_groups(user=api.user.get_current())
    orgs = organizations_with_suffixes(groups, suffixes)
    ret = {'assigned_group': {'query': orgs}}
    return ret


class TaskValidationCriterion(object):
    """
        Return catalog criteria following validation group member
    """

    def __init__(self, context):
        self.context = context

    @property
    def query(self):
        return validation_criterion(self.context, ['validateur'])


class UserIsAdministrativeResponsibleCriterion(object):

    def __init__(self, context):
        self.context = context

    @property
    def query(self):
        groups = api.group.get_groups(user=api.user.get_current())
        orgs = organizations_with_suffixes(groups, ['admin_resp'])
        # if orgs is empty list, nothing is returned => ok
        return {'administrative_responsible': {'query': orgs}}


class UserIsActionEditorCriterion(object):

    def __init__(self, context):
        self.context = context

    @property
    def query(self):
        groups = api.group.get_groups(user=api.user.get_current())
        orgs = organizations_with_suffixes(groups, ['actioneditor'])
        # if orgs is empty list, nothing is returned => ok
        return {'manager': {'query': orgs}}


class TaskInAssignedGroupCriterion(object):
    """Return catalog criteria following assigned group member."""

    def __init__(self, context):
        self.context = context

    @property
    def query(self):
        groups = api.group.get_groups(user=api.user.get_current())
        orgs = organizations_with_suffixes(groups, ['validateur', 'editeur', 'actioneditor'])
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
    if hasattr(obj, 'categories') and obj.categories:
        return obj.categories

    return common_marker


@indexer(IContentish)
def priority_index(obj):
    if base_hasattr(obj, 'priority') and obj.priority:
        return obj.priority

    return common_marker


@indexer(IContentish)
def representative_responsible_index(obj):
    if base_hasattr(obj, 'representative_responsible') and obj.representative_responsible:
        return obj.representative_responsible
    if obj.portal_type == 'pstaction':
        oo = obj.aq_inner.aq_parent
        if oo.representative_responsible:
            return oo.representative_responsible
    if obj.portal_type == 'pstsubaction':
        oo = obj.aq_inner.aq_parent.aq_parent
        if oo.representative_responsible:
            return oo.representative_responsible

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


@indexer(IPSTAction)
def responsible_index(obj):
    if base_hasattr(obj, 'responsible') and obj.responsible:
        return obj.responsible

    return EMPTY_STRING


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


@indexer(ITask)
def directly_in_pstaction_index(obj):
    inner = obj.aq_inner
    iter = inner

    while iter is not None:
        if IPSTSubAction.providedBy(iter):
            return False
        if IPSTAction.providedBy(iter):
            return True
        if ISiteRoot.providedBy(iter):
            return False

        if not hasattr(iter, "aq_parent"):
            raise RuntimeError("Parent traversing interrupted by object: " + str(iter))

        iter = iter.aq_parent


@indexer(IContentish)
def plan_index(obj):
    if hasattr(obj, 'plan') and obj.plan:
        return obj.plan

    return common_marker


################
# GUI cleaning #
################


class ActionsSubMenuItem(OrigActionsSubMenuItem):

    def available(self):
        # plone.api.user.has_permission doesn't work with zope admin
        if not getSecurityManager().checkPermission('Manage portal', self.context):
            return False
        return super(ActionsSubMenuItem, self).available()


class FactoriesSubMenuItem(OrigFactoriesSubMenuItem):

    def available(self):
        # plone.api.user.has_permission doesn't work with zope admin
        if not getSecurityManager().checkPermission('Manage portal', self.context):
            return False
        return super(FactoriesSubMenuItem, self).available()


class WorkflowMenu(OrigWorkflowMenu):

    def getMenuItems(self, context, request):
        if not getSecurityManager().checkPermission('Manage portal', context):
            return []
        return super(WorkflowMenu, self).getMenuItems(context, request)
