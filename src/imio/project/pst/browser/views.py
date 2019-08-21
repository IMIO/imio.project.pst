# -*- coding: utf-8 -*-

from collective.eeafaceted.dashboard.browser.overrides import DashboardFacetedTableView as DFTV
from imio.helpers.content import transitions
from plone import api
from plone.app.versioningbehavior.browser import VersionView as OVV
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


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
        new_pst.budget_years = [2019, 2020, 2021, 2022, 2023, 2024]
        new_pst.restrictedTraverse('clean_budget/delete')()
        transitions(new_pst, ['publish_internally'])
        return self.request.RESPONSE.redirect(new_pst.absolute_url())


class VersionView(OVV):
    """ override of call from 1.2.10 """

    def __call__(self):
        version_id = self.request.get('version_id', None)
        if not version_id:
            raise ValueError(u'Missing parameter on the request: version_id')

        content_core_view = getMultiAdapter((self.context, self.request), name='content-core-version')
        html = content_core_view()
        return self._convert_download_links(html, version_id)


class OSOOFacetedTableView(DFTV):
    """ """

    def _getViewFields(self):
        """Returns fields we want to show in the table."""
        # selectedViewFields is a list of tuples (id, title)
        return [elt[0] for elt in self.collection.selectedViewFields() if elt[0] != 'parents']
