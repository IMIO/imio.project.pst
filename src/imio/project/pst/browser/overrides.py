# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from Acquisition import aq_inner
from collective.contact.widget.interfaces import IContactContent
from collective.task.interfaces import ITaskContent
from imio.history.browser.views import IHDocumentBylineViewlet
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.core.content.project import IProject
from plone.app.contenttypes.interfaces import IDocument
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IFolder
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.viewlets.common import ContentActionsViewlet as CAV
from plone.app.layout.viewlets.common import PathBarViewlet as PBV
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import get_view_url
from Products.CMFPlone.browser.ploneview import Plone as PV
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.interface import implements


class DocumentBylineViewlet(IHDocumentBylineViewlet):
    '''
      Overrides the IHDocumentBylineViewlet to hide it for some layouts.
    '''

    def show(self):
        currentLayout = self.context.getLayout()
        if currentLayout in ['facetednavigation_view', ] or self.context.portal_type in ('projectspace', ):
            return False
        return True


class PhysicalNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

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
            base += ({'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context),
                      'ct_class': 'contenttype-{}'.format(context.portal_type)},
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
