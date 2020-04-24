# -*- coding: utf-8 -*-

from Products.CMFPlone.utils import base_hasattr
from Products.statusmessages.interfaces import IStatusMessage
from collective.eeafaceted.dashboard.browser.overrides import DashboardFacetedTableView as DFTV
from collective.z3cform.datagridfield import DataGridFieldFactory
from imio.helpers.content import transitions
from imio.project.core.config import SUMMARIZED_FIELDS
from imio.project.pst import _
from imio.project.pst.content.action import IPSTAction
from plone import api
from plone.app.versioningbehavior.browser import VersionView as OVV
from Products.Five.browser import BrowserView
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.form import EditForm
from z3c.form.interfaces import HIDDEN_MODE
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
        self.context.title = u'PST 2013-2018'
        self.context.reindexObject()
        new_pst = api.content.rename(new_pst, 'pst')
        new_pst.title = u'PST 2019-2024'
        new_pst.manage_addLocalRoles("pst_editors", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))
        new_pst.reindexObject()
        new_pst.reindexObjectSecurity()
        new_pst.budget_years = [2019, 2020, 2021, 2022, 2023, 2024]
        del_view = new_pst.restrictedTraverse('clean_budget/delete')
        for fld in SUMMARIZED_FIELDS:
            del_view(fld)
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
        """ We don't show parents column """
        return [elt[0] for elt in self.collection.selectedViewFields() if elt[0] != 'parents']


class ActionFacetedTableView(DFTV):
    """ """

    def _getViewFields(self):
        """ We don"t show parents column on an action with tasks """
        if self.context.portal_type == 'pstsubaction' or not self.request.get('has_subaction'):
            return [elt[0] for elt in self.collection.selectedViewFields()]
        else:
            return [elt[0] for elt in self.collection.selectedViewFields() if elt[0] != 'parents']


class BudgetSplitForm(EditForm):

    label = _(u"Split action budget")
    fields = Fields(IPSTAction).select('budget_split')
    fields['budget_split'].widgetFactory = DataGridFieldFactory

    def getContent(self):
        if base_hasattr(self.context, 'symbolic_link'):
            return self.context._link
        else:
            return self.context

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Budget split saved"),
            "info",
        )

    def datagridUpdateWidgets(self, subform, widgets, widget):
        widget.columns[0]['mode'] = HIDDEN_MODE
        widgets['uid'].mode = HIDDEN_MODE
    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.widgets['budget_split'].allow_reorder = False
        self.widgets['budget_split'].allow_insert = False
        self.widgets['budget_split'].allow_delete = False
        self.widgets['budget_split'].auto_append = False
