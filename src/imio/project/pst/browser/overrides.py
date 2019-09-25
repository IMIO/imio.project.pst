# -*- coding: utf-8 -*-
#
# File: overrides.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from Acquisition import aq_inner
from imio.history.browser.views import IHDocumentBylineViewlet
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.viewlets.common import PathBarViewlet as PBV
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import get_view_url
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
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
