# -*- coding: utf-8 -*-
from plone.memoize import ram
from Products.CMFPlone.utils import getToolByName

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
    ordered_states = {
        'strategicobjective': pst_objective_wf_order,
        'operationalobjective': pst_objective_wf_order,
        'pstaction': [
            'created',
            'to_be_scheduled',
            'ongoing',
            'terminated',
            'stopped',
        ],
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
    pw = getToolByName(context, 'portal_workflow')
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
