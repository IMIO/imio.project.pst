# -*- coding: utf-8 -*-

from imio.helpers.xhtml import object_link
from imio.project.core.config import SUMMARIZED_FIELDS
from plone import api
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser import BrowserView
from zope.annotation import IAnnotations


class CleanBudget(BrowserView):
    """ IImioPSTProject view to manage budget related """

    def delete(self, field, empty_budget='1'):
        """
            Deletes project types budget fields and deletes parents budgets infos.
            Used in archive action too.
        """
        ret = []
        AK = SUMMARIZED_FIELDS[field]
        b_c = a_c = 0
        path = '/'.join(self.context.getPhysicalPath())
        years = self.context.budget_years
        for pt in ('pstsubaction', 'pstaction', 'operationalobjective', 'strategicobjective'):
            for brain in self.context.portal_catalog(portal_type=pt, path=path, sort_on='path'):
                obj = brain.getObject()
                # ret.append("{}: {} = {}".format(pt, brain.getPath(), obj.budget))
                if base_hasattr(obj, field) and getattr(obj, field) and empty_budget:
                    b_c += 1
                    prt = False
                    for dic in getattr(obj, field):
                        if dic['year'] in years:
                            prt = True
                            break
                    if prt:
                        ret.append("{}: {}".format(object_link(obj).encode('utf8'), getattr(obj, field)))
                    setattr(obj, field, [])
                obj_annotations = IAnnotations(obj)
                if AK in obj_annotations:
                    if obj_annotations[AK]:
                        a_c += 1
                    del obj_annotations[AK]
        msg = '{} field cleaned on {} fields and {} parents annotations'.format(field, b_c, a_c)
        ret.append("\n" + msg)
        return '<br />\n'.join(ret)
        api.portal.show_message(msg, self.request)
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def display(self, field):
        """ Display budget fields and annotations """
        AK = SUMMARIZED_FIELDS[field]
        b_c = a_c = u_c = 0
        bret = ['Budget fields']
        cret = ['Budget annotations']
        path = '/'.join(self.context.getPhysicalPath())
        lpath = len(path)
        pt = ('pstsubaction', 'pstaction', 'operationalobjective', 'strategicobjective')
        for brain in self.context.portal_catalog(portal_type=pt, path=path, sort_on='path'):
            obj = brain.getObject()
            if base_hasattr(obj, field) and getattr(obj, field):
                b_c += 1
                bret.append("{}: {} = {}".format(object_link(obj, content=brain.getPath()[lpath:]).encode('utf-8'),
                                                 brain.UID, getattr(obj, field)))
            obj_annotations = IAnnotations(obj)
            if AK in obj_annotations and obj_annotations[AK]:
                a_c += 1
                u_c += len([uid for uid in obj_annotations[AK] if obj_annotations[AK][uid]])
                cret.append("{}: {}".format(object_link(obj, content=brain.getPath()[lpath:]).encode('utf-8'),
                                            obj_annotations[AK]))
        sep = '<br />\n'
        return sep.join(['b:{}, a:{}, u:{}'.format(b_c, a_c, u_c), ''] + bret + [''] + cret)

    def clean(self, field):
        """ Cleans budget fields and annotations of unrelated things """
        AK = SUMMARIZED_FIELDS[field]
        ret = ['Cleaning']
        path = '/'.join(self.context.getPhysicalPath())
        lpath = len(path)
        years = self.context.budget_years
        for pt in ('pstsubaction', 'pstaction', 'operationalobjective', 'strategicobjective'):
            for brain in self.context.portal_catalog(portal_type=pt, path=path, sort_on='path'):
                obj = brain.getObject()
                # ret.append("{}: {} = {}".format(pt, brain.getPath(), obj.budget))
                if base_hasattr(obj, field) and getattr(obj, field):
                    new_budget = []
                    for dic in getattr(obj, field):
                        if dic['year'] in years:
                            new_budget.append(dic)
                    if len(getattr(obj, field)) != len(new_budget):
                        ret.append("B, {}: {} => {}".format(object_link(obj,
                                                                        content=brain.getPath()[lpath:]).encode('utf8'),
                                                            getattr(obj, field), new_budget))
                        setattr(obj, field, new_budget)
                obj_annotations = IAnnotations(obj)
                if AK not in obj_annotations:
                    continue
                new_annot = {}
                for uid in obj_annotations[AK]:
                    if not obj_annotations[AK][uid]:
                        continue
                    brains = api.content.find(UID=uid, path=path)
                    if not brains:
                        ret.append("C, {}: {}".format(object_link(obj, content=brain.getPath()[lpath:]).encode('utf8'),
                                                      uid))
                        continue
                    new_annot[uid] = obj_annotations[AK][uid]
                if len(new_annot) != len(obj_annotations[AK]):
                    obj_annotations[AK] = new_annot
        return '<br />\n'.join(ret)
