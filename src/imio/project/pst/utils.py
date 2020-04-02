# -*- coding: utf-8 -*-
from imio.project.pst.interfaces import IImioPSTProject
from plone import api
from plone.memoize import ram
from Products.Five import BrowserView

from collective.contact.plonegroup.utils import organizations_with_suffixes
from imio.helpers.cache import get_cachekey_volatile


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
        return IImioPSTProject.providedBy(self.context)
