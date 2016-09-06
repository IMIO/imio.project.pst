from plone.memoize import forever


@forever.memoize
def _getWorkflowStates(portal, portal_type, skip_initial=False, skip_states=[]):
    """
        Return a list of a portal_type workflow states
    """
    pwkf = portal.portal_workflow
    ret = []
    workflows = pwkf.getChainForPortalType(portal_type)
    if not workflows:
        return ret
    workflow = pwkf[workflows[0]]
    for state in workflow.states:
        if skip_initial and state == workflow.initial_state:
            continue
        if skip_states and state in skip_states:
            continue
        ret.append(state)
    return ret
