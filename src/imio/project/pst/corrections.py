# -*- coding: utf-8 -*-

from imio.project.core.config import CHILDREN_BUDGET_INFOS_ANNOTATION_KEY
from plone import api
from Products.Five.browser import BrowserView
from zope.annotation import IAnnotations


class CleanBudget(BrowserView):
    """ Clean budget field of project types and clean parents budgets infos """

    def __call__(self):
        ret = []
        b_c = p_c = 0
        path = '/'.join(self.context.getPhysicalPath())
        for pt in ('pstaction', 'operationalobjective', 'strategicobjective'):
            for brain in self.context.portal_catalog(portal_type=pt, path=path, sort_on='path'):
                obj = brain.getObject()
                ret.append("{}: {} = {}".format(pt, brain.getPath(), obj.budget))
                if obj.budget:
                    b_c += 1
                    obj.budget = []
                obj_annotations = IAnnotations(obj)
                if CHILDREN_BUDGET_INFOS_ANNOTATION_KEY in obj_annotations:
                    p_c += 1
                    del obj_annotations[CHILDREN_BUDGET_INFOS_ANNOTATION_KEY]
        api.portal.show_message('Budget cleaned on {} fields and {} parents annotations'.format(b_c, p_c),
                                self.request)
#        return '\n'.join(ret)
        return self.request.RESPONSE.redirect(self.context.absolute_url())
