# -*- coding: utf-8 -*-

from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from plone import api
from Products.Five.browser import BrowserView


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


class ArchiveView(BrowserView):
    """
        Common methods
    """

    def archive(self):
        """ """
        portal = api.portal.get()
        new_pst = api.content.copy(self.context, portal, 'pst-tmp', False)
        self.context = api.content.rename(self.context, 'pst-2012-2018')
        self.context.title = u'PST (2012-2018)'
        self.context.reindexObject()
        new_pst = api.content.rename(new_pst, 'pst')
        new_pst.title = u'PST (2018-2024)'
        new_pst.manage_addLocalRoles("pst_editors", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))
        new_pst.reindexObject()
        new_pst.reindexObjectSecurity()
        path = '/'.join(self.context.getPhysicalPath())
        for brain in portal.portal_catalog(path=path, portal_type='DashboardCollection'):
            obj = brain.getObject()
            query = obj.query
            for elt in query:
                if elt['i'] == 'path':
                    elt['v'] = path
            obj.query = query
        for obj in [new_pst.strategicobjectives, new_pst.operationalobjectives, new_pst.pstactions,
                    new_pst.tasks]:
            default_col = obj['all'].UID()  # could be dynamic... base on relative path to old uid
            _updateDefaultCollectionFor(obj, default_col)
        new_pst.budget_years = [2019, 2020, 2021, 2022, 2023, 2024]
        return self.request.RESPONSE.redirect(new_pst.absolute_url())
