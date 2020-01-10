# -*- coding: utf-8 -*-

from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SitemapView(BrowserView):

    recurse = ViewPageTemplateFile('projectspace_sitemap_recurse.pt')

    def navigation_tree_rec(self, context=None):
        if not context:
            context = self.context
        return {
            'element': context,
            'state': api.content.get_state(context, 'no'),
            'children': [self.navigation_tree_rec(child) for child in self.children(context)],
        }

    def children(self, context):
        filters = {
            'projectspace': {"portal_type": 'strategicobjective'},
            'strategicobjective': {"portal_type": 'operationalobjective'},
            'operationalobjective': {"portal_type": 'pstaction'},
            'pstaction': {"portal_type": ['pstsubaction', 'task']},
            'pstsubaction': {"portal_type": 'task'},
        }

        return context.listFolderContents(filters.get(context.portal_type, {}))
