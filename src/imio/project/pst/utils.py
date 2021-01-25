# -*- coding: utf-8 -*-
from datetime import date

from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.pst.content.pstprojectspace import IPSTProjectSpace
from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from Products.Five import BrowserView

from collective.contact.plonegroup.utils import organizations_with_suffixes
from imio.helpers.cache import get_cachekey_volatile
from zope.component import getUtility


EMPTY_DATE = date(1950, 1, 1)


def list_wf_states_cache_key(function, context, portal_type):
    return get_cachekey_volatile("%s.%s" % (function.func_name, portal_type))


@ram.cache(list_wf_states_cache_key)
def list_wf_states(context, portal_type):
    """
        list all portal_type wf states
    """

    pst_objective_wf_order = [
        'created',
        'ongoing',
        'achieved',
    ]
    pst_action_wf_order = [
        'created',
        'to_be_scheduled',
        'ongoing',
        'terminated',
        'stopped',
    ]
    ordered_states = {
        'strategicobjective': pst_objective_wf_order,
        'operationalobjective': pst_objective_wf_order,
        'pstaction': pst_action_wf_order,
        'pstsubaction': pst_action_wf_order,
        'task': [
            'created',
            'to_assign',
            'to_do',
            'in_progress',
            'realized',
            'closed',
        ],
    }

    if portal_type not in ordered_states:
        return []
    pw = api.portal.get_tool('portal_workflow')
    ret = []
    # wf states
    for workflow in pw.getWorkflowsFor(portal_type):
        state_ids = [value.id for value in workflow.states.values()]
        break
    # keep ordered states
    for state in ordered_states[portal_type]:
        if state in state_ids:
            ret.append(state)
            state_ids.remove(state)
    # add missing
    for missing in state_ids:
        ret.append(missing)
    return ret


def filter_states(context, portal_type, skip_states=[]):
    """
        Return a list of filtered states
    """
    states = list_wf_states(context, portal_type)
    if skip_states:
        return [st for st in states if st not in skip_states]
    return states


def get_echevins_config(site):
    """
    Get an (id, uid) dictionary of echevins config.
    :param site: The portal root
    :return: Echevins dict
    :rtype: dict
    """
    echevins_organisation = site.contacts['plonegroup-organization']['echevins']
    echevins_dict = {}
    for obj in echevins_organisation.objectValues():
        echevins_dict[obj.id] = obj.UID()
    return echevins_dict


def get_services_config():
    """
    Get an (id, uid) dictionary of services config.
    :return: Services dict
    :rtype: dict
    """
    registry = getUtility(IRegistry)
    services_dict = {}
    for uid in registry[ORGANIZATIONS_REGISTRY]:
        service_organisation = uuidToObject(uid)
        services_dict[service_organisation.id] = uid
    return services_dict


def find_deadlines_on_children(context=None, query=None):
    """
    Find deadlines on children.
    :param context: Context for the search
    :type context: Content object
    :param query: All children's key pair values (portal types and deadline field name).
    :type query: Dict
    :returns: deadlines (zope.schema._field.Datetime)
    :rtype: List
    :Example: query = {"operationalobjective": "planned_end_date", "pstaction": "planned_end_date", "task": "due_date"}
    """
    deadlines = []
    brains = api.content.find(context=context, portal_typ=query.keys())
    for brain in brains:
        for item in query.items():
            if brain.portal_type == item[0]:
                if getattr(brain, item[1]):
                    if getattr(brain, item[1]) != EMPTY_DATE:
                        deadlines.append(getattr(brain, item[1]))
                        break
    return deadlines


def find_max_deadline_on_children(context=None, query=None):
    """
    Find max deadline on children.
    :param context: Context for the search
    :type context: Content object
    :param query: All children's key pair values (portal types and deadline field name).
    :type query: Dict
    :returns: max deadline (zope.schema._field.Datetime), or None
    :rtype: zope.schema.Date
    :Example: query = {"operationalobjective": "planned_end_date", "pstaction": "planned_end_date", "task": "due_date"}
    """
    max_deadline = None
    deadlines = find_deadlines_on_children(context, query)
    if deadlines:
        max_deadline = max(deadlines)
    return max_deadline


def find_brains_on_parents(context=None):
    """
    Find brains on parent.
    :param context: Context for the search
    :type context: Content object
    :returns: List of Catalog brains
    :rtype: List
    """
    parent_brains = []
    parent = context.__parent__
    while not IProjectSpace.providedBy(parent) and parent.portal_type != 'Plone Site':
        parent_brains.append(api.content.find(parent, depth=0))
        parent = parent.__parent__
    return parent_brains


def find_deadlines_on_parents(context=None, query=None):
    """
    Find deadlines on parents.
    :param context: Context for the search
    :type context: Content object
    :param query: All parents key pair values (portal types and deadline field name).
    :type query: Dict
    :returns: deadlines (zope.schema._field.Datetime)
    :rtype: List
    :Example: query = {"operationalobjective": "planned_end_date", "pstaction": "planned_end_date", "task": "due_date"}
    """
    deadlines = []
    parent_brains = find_brains_on_parents(context)
    for brains in parent_brains:
        for item in query.items():
            if brains[0].portal_type == item[0]:
                if getattr(brains[0], item[1]):
                    if getattr(brains[0], item[1]) != EMPTY_DATE:
                        deadlines.append(getattr(brains[0], item[1]))
                        break
    return deadlines


def is_smaller_deadline_on_parents(context=None, query=None):
    """
    Find smaller deadline on the parents.
    :param context: Context for the search
    :type context: Content object
    :param query: All parents key pair values (portal types and deadline field name).
    :type query: Dict
    :returns: True if there is smaller date on parents or False
    :rtype: bool
    :Example: query = {"operationalobjective": "planned_end_date", "pstaction": "planned_end_date", "task": "due_date"}
    """
    is_smaller_deadline = False
    deadlines = find_deadlines_on_parents(context, query)
    if deadlines:
        for deadline in deadlines:
            for item in query.items():
                if context.portal_type == item[0]:
                    if getattr(context, item[1]):
                        if getattr(context, item[1]) != EMPTY_DATE:
                            if deadline < getattr(context, item[1]):
                                is_smaller_deadline = True
                                break
            if is_smaller_deadline:
                break
    return is_smaller_deadline


# views

class UtilsMethods(BrowserView):
    """ View containing utils methods """

    def user_is_admin(self):
        """ Test if current user is admin """
        user = api.user.get_current()
        if user.has_role(['Manager', 'Site Administrator']):
            return True
        return False

    def current_user_groups(self, user):
        """ Return current user groups """
        return api.group.get_groups(user=user)

    def current_user_groups_ids(self, user):
        """ Return current user groups ids """
        return [g.id for g in self.current_user_groups(user)]

    def user_has_review_level(self, suffixes=['validateur']):
        """ Test if the current user has a review level """
        groups = api.group.get_groups(user=api.user.get_current())
        orgs = organizations_with_suffixes(groups, suffixes)
        return (orgs and True or False)

    def is_in_user_groups(self, groups=[], admin=True, test='any', user=None):
        """ Test if one or all of a given group list is part of the current user groups """
        # for admin, we bypass the check
        if admin and self.user_is_admin():
            return True
        if not user:
            user = api.user.get_current()
        u_groups = self.current_user_groups_ids(user)
        if test == 'any':
            return any(x in u_groups for x in groups)
        elif test == 'all':
            return all(x in u_groups for x in groups)
        return False

    def is_pst_project(self):
        """ """
        return IPSTProjectSpace.providedBy(self.context)
