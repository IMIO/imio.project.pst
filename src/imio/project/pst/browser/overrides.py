# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from plone.app.controlpanel.usergroups import GroupsOverviewControlPanel
from plone.app.controlpanel.usergroups import UsersGroupsControlPanelView
from plone.app.controlpanel.usergroups import UsersOverviewControlPanel

from Acquisition import aq_inner
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import get_view_url
from Products.CMFPlone.browser.ploneview import Plone as PV
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import base_hasattr
from Products.CPUtils.Extensions.utils import check_zope_admin
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.contact.widget.interfaces import IContactContent
from collective.task.interfaces import ITaskContent
from imio.history.browser.views import IHDocumentBylineViewlet
from imio.project.core.content.project import IProject
from imio.project.core.content.projectspace import IProjectSpace
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IFolder
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.viewlets.common import ContentActionsViewlet as CAV
from plone.app.layout.viewlets.common import PathBarViewlet as PBV
from zope.component import getMultiAdapter
from zope.interface import implementer


class DocumentBylineViewlet(IHDocumentBylineViewlet):
    '''
      Overrides the IHDocumentBylineViewlet to hide it for some layouts.
    '''

    def show(self):
        currentLayout = self.context.getLayout()
        if currentLayout in ['facetednavigation_view', ] or IProjectSpace.providedBy(self.context):
            return False
        return True


@implementer(INavigationBreadcrumbs)
class PhysicalNavigationBreadcrumbs(BrowserView):

    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = utils.parent(context)

        name, item_url = get_view_url(context)

        if container is None:
            return ({'absolute_url': item_url,
                     'Title': utils.pretty_title_or_id(context, context),
                     'ct_class': 'contenttype-{}'.format(context.portal_type)},
                    )

        view = getMultiAdapter((container, request), name='breadcrumbs_view')
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation
        # root
        if not utils.isDefaultPage(context, request) \
                and not rootPath.startswith(itemPath):
            portal_type = context.portal_type
            if base_hasattr(context, '_link_portal_type'):
                portal_type = context._link_portal_type
            base += ({'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context),
                      'ct_class': 'contenttype-{}'.format(portal_type)},
                     )

        return base


class PathBarViewlet(PBV):
    index = ViewPageTemplateFile('templates/path_bar.pt')


class Plone(PV):

    def showEditableBorder(self):
        context = aq_inner(self.context)
        for interface in (IProject, IProjectSpace, ITaskContent, IContactContent, IFile, IFolder):
            if interface.providedBy(context):
                return False
        return super(Plone, self).showEditableBorder()


class ContentActionsViewlet(CAV):
    """ """
    def render(self):
        context = aq_inner(self.context)
        for interface in (IDocument, IPloneSiteRoot):
            if interface.providedBy(context):
                return ''
        return self.index()


class BaseOverviewControlPanel(UsersGroupsControlPanelView):
    """Override to filter result and remove every selectable roles."""

    @property
    def portal_roles(self):
        return ['Manager', 'Member', 'Site Administrator']

    def doSearch(self, searchString):
        results = super(BaseOverviewControlPanel, self).doSearch(searchString)
        if check_zope_admin:
            return results
        adapted_results = []
        for item in results:
            adapted_item = item.copy()
            for role in self.portal_roles:
                adapted_item['roles'][role]['canAssign'] = False
            adapted_results.append(adapted_item)
        return adapted_results


class PSTUsersOverviewControlPanel(BaseOverviewControlPanel, UsersOverviewControlPanel):
    """See PMBaseOverviewControlPanel docstring."""


class PSTGroupsOverviewControlPanel(BaseOverviewControlPanel, GroupsOverviewControlPanel):
    """See PMBaseOverviewControlPanel docstring."""

    @property
    def portal_roles(self):
        return ['Manager', 'Site Administrator']
