# -*- coding: utf-8 -*-

from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.annotation import IAnnotations
from zope.component import getMultiAdapter

WS4PMCLIENT_ANNOTATION_KEY = "imio.pm.wsclient-sent_to"

class ExportDelibPointsView(BrowserView):

    def __call__(self):
        portal = api.portal.get()
        ws4pmSettings = getMultiAdapter((portal, self.request), name='ws4pmclient-settings')
        
        
        anno = IAnnotations(self.context)

        rows = ["content_uid, delib_points_uids"]
        brains = api.content.find(portal_type=['pstaction', 'pstsubaction', 'task'])
        for b in brains:
            obj = b.getObject()
            obj_anno = IAnnotations(obj)
            if WS4PMCLIENT_ANNOTATION_KEY in obj_anno:
                points = ws4pmSettings._soap_searchItems({'externalIdentifier': obj.UID()})
                points_uids = [p['UID'] for p in points]
                rows.append("{}, {}".format(obj.UID(), ';'.join(points_uids)))
        output = "\n".join(rows)
        self.request.response.setHeader('Content-Type', 'text/csv')
        self.request.response.setHeader('Content-Disposition', 'attachment; filename="export-delib-points.csv"')
        return output
