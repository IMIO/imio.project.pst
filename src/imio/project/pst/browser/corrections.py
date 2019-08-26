# -*- coding: utf-8 -*-

from imio.helpers.xhtml import object_link
from imio.project.core.config import CHILDREN_BUDGET_INFOS_ANNOTATION_KEY as CBIAK
from plone import api
from Products.Five.browser import BrowserView
from zope.annotation import IAnnotations


class CleanBudget(BrowserView):
    """ IImioPSTProject view to manage budget related """

    def delete(self):
        """
            Deletes project types budget fields and deletes parents budgets infos.
            Used in archive action too.
        """
        ret = []
        b_c = a_c = 0
        path = '/'.join(self.context.getPhysicalPath())
        years = self.context.budget_years
        for pt in ('pstaction', 'operationalobjective', 'strategicobjective'):
            for brain in self.context.portal_catalog(portal_type=pt, path=path, sort_on='path'):
                obj = brain.getObject()
                # ret.append("{}: {} = {}".format(pt, brain.getPath(), obj.budget))
                if obj.budget:
                    b_c += 1
                    prt = False
                    for dic in obj.budget:
                        if dic['year'] in years:
                            prt = True
                            break
                    if prt:
                        ret.append("{}: {}".format(object_link(obj).encode('utf8'), obj.budget))
                    obj.budget = []
                obj_annotations = IAnnotations(obj)
                if CBIAK in obj_annotations:
                    if obj_annotations[CBIAK]:
                        a_c += 1
                    del obj_annotations[CBIAK]
        api.portal.show_message('Budget cleaned on {} fields and {} parents annotations'.format(b_c, a_c),
                                self.request)
        return '<br />\n'.join(ret)
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def display(self):
        """ Display budget fields and annotations """
        b_c = a_c = u_c = 0
        bret = ['Budget fields']
        cret = ['Budget annotations']
        path = '/'.join(self.context.getPhysicalPath())
        lpath = len(path)
        pt = ('pstaction', 'operationalobjective', 'strategicobjective')
        for brain in self.context.portal_catalog(portal_type=pt, path=path, sort_on='path'):
            obj = brain.getObject()
            if obj.budget:
                b_c += 1
                bret.append("{}: {} = {}".format(object_link(obj, content=brain.getPath()[lpath:]).encode('utf-8'),
                                                 brain.UID, obj.budget))
            obj_annotations = IAnnotations(obj)
            if CBIAK in obj_annotations and obj_annotations[CBIAK]:
                a_c += 1
                u_c += len(obj_annotations[CBIAK])
                cret.append("{}: {}".format(object_link(obj, content=brain.getPath()[lpath:]).encode('utf-8'),
                                            obj_annotations[CBIAK]))
        sep = '<br />\n'
        return sep.join(['b:{}, a:{}, u:{}'.format(b_c, a_c, u_c), ''] + bret + [''] + cret)

    def clean(self):
        """ Cleans budget fields and annotations of unrelated things """
        ret = ['Cleaning']
        path = '/'.join(self.context.getPhysicalPath())
        lpath = len(path)
        years = self.context.budget_years
        for pt in ('pstaction', 'operationalobjective', 'strategicobjective'):
            for brain in self.context.portal_catalog(portal_type=pt, path=path, sort_on='path'):
                obj = brain.getObject()
                # ret.append("{}: {} = {}".format(pt, brain.getPath(), obj.budget))
                if obj.budget:
                    new_budget = []
                    for dic in obj.budget:
                        if dic['year'] in years:
                            new_budget.append(dic)
                    if len(obj.budget) != len(new_budget):
                        ret.append("B, {}: {} => {}".format(object_link(obj,
                                                                        content=brain.getPath()[lpath:]).encode('utf8'),
                                                            obj.budget, new_budget))
                        obj.budget = new_budget
                obj_annotations = IAnnotations(obj)
                if CBIAK not in obj_annotations:
                    continue
                new_annot = {}
                for uid in obj_annotations[CBIAK]:
                    if not obj_annotations[CBIAK][uid]:
                        continue
                    brains = api.content.find(UID=uid, path=path)
                    if not brains:
                        ret.append("C, {}: {}".format(object_link(obj, content=brain.getPath()[lpath:]).encode('utf8'),
                                                      uid))
                        continue
                    new_annot[uid] = obj_annotations[CBIAK][uid]
                if len(new_annot) != len(obj_annotations[CBIAK]):
                    obj_annotations[CBIAK] = new_annot
        return '<br />\n'.join(ret)