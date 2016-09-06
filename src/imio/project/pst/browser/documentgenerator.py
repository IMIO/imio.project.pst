# -*- coding: utf-8 -*-

from zope.annotation import IAnnotations

from collective.documentgenerator.helper.dexterity import DXDocumentGenerationHelperView
from imio.project.core.config import CHILDREN_BUDGET_INFOS_ANNOTATION_KEY

from views import _getWorkflowStates


class DocumentGenerationPSTHelper(DXDocumentGenerationHelperView):
    """
        Methods used in document generation view, for pst
    """

    def getStrategicObjectives(self):
        """
            get a list of contained strategic objectives
        """
        pcat = self.context.portal_catalog
        brains = pcat(portal_type='strategicobjective',
                      path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
                      review_state=_getWorkflowStates(self.portal, 'strategicobjective', skip_initial=True),
                      sort_on='getObjPositionInParent')
        sos = []
        for brain in brains:
            obj = brain.getObject()
            sos.append(obj)
        return sos

    def getOperationalObjectives(self, so=None):
        """
            get a list of contained operational objectives
        """
        oos = self.getDGHV(so).getOperationalObjectives()
        return oos

    def getActions(self, oo=None):
        """
            return a list of contained pstactions
        """
        acts = self.getDGHV(oo).getActions()
        return acts


class BudgetHelper():
    """
        Budget helper methods
    """
    def getOwnBudget(self):
        """
            get the own rendered widget
        """
        soup = self.display_widget('budget', soup=True)
        return str(soup.find('fieldset').find('table'))

    def getChildrenBudget(self):
        """
            get the children budget
        """
        soup = self.display_widget('budget', soup=True)
        return str(soup.find('table', class_='budgetinfos_table'))

    def hasChildrenBudget(self, obj):
        """
            has children budget ?
        """
        obj_annotations = IAnnotations(obj)
        if CHILDREN_BUDGET_INFOS_ANNOTATION_KEY in obj_annotations:
            for uid in obj_annotations[CHILDREN_BUDGET_INFOS_ANNOTATION_KEY]:
                if obj_annotations[CHILDREN_BUDGET_INFOS_ANNOTATION_KEY][uid]:
                    return True
        return False


class DocumentGenerationSOHelper(DXDocumentGenerationHelperView, BudgetHelper):
    """
        Methods used in document generation view, for strategicobjective
    """

    def getStrategicObjectives(self):
        """
            get a list of unique contained strategic objective
        """
        return [self.real_context]

    def getOperationalObjectives(self, so=None):
        """
            get a list of contained operational objectives
        """
        pcat = self.real_context.portal_catalog
        brains = pcat(portal_type='operationalobjective',
                      path={'query': '/'.join(self.real_context.getPhysicalPath()), 'depth': 1},
                      review_state=_getWorkflowStates(self.portal, 'operationalobjective', skip_initial=True),
                      sort_on='getObjPositionInParent')
        oos = []
        for brain in brains:
            oos.append(brain.getObject())
        return oos

    def getActions(self, oo=None):
        """
            return a list of contained pstactions
        """
        acts = self.getDGHV(oo).getActions()
        return acts

    def getSection(self):
        """
            get the first part of a category value
        """
        try:
            return self.display_voc('categories').split(' - ')[0]
        except IndexError:
            return ''

    def getDomain(self):
        """
            get the second part of a category value
        """
        try:
            return self.display_voc('categories').split(' - ')[1]
        except IndexError:
            return ''


class DocumentGenerationOOHelper(DXDocumentGenerationHelperView, BudgetHelper):
    """
        Methods used in document generation view, for operationalobjective
    """

    def getStrategicObjectives(self):
        """
            get a list of the parent strategic objective of the current operationalobjective
        """
        return [self.real_context.aq_inner.aq_parent]

    def getOperationalObjectives(self, so=None):
        """
            get a list of an unique contained operational objective
        """
        return [self.real_context]

    def getActions(self, oo=None):
        """
            return a list of contained pstactions
        """
        pcat = self.real_context.portal_catalog
        brains = pcat(portal_type='pstaction',
                      path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
                      review_state=_getWorkflowStates(self.portal, 'pstaction', skip_initial=True),
                      sort_on='getObjPositionInParent')
        return [brain.getObject() for brain in brains]

    def formatResultIndicator(self, expected=True, sep='<br />'):
        """
            return the result indicator as a string
        """
        rows = []
        for row in self.real_context.result_indicator:
            rows.append("%s = %d" % (row['label'].encode('utf8'), expected and row['value'] or row['reached_value']))
        return sep.join(rows)


class DocumentGenerationPSTActionsHelper(DXDocumentGenerationHelperView, BudgetHelper):
    """
        Methods used in document generation view, for PSTAction
    """

    def getStrategicObjectives(self):
        """
            get a list of the parent strategic objective of the current operationalobjective
        """
        return [self.real_context.aq_inner.aq_parent.aq_inner.aq_parent]

    def getOperationalObjectives(self, so=None):
        """
            get a list of an unique contained operational objective
        """
        return [self.real_context.aq_inner.aq_parent]

    def getActions(self, oo=None):
        """
            return a list of contained pstactions
        """
        return [self.real_context]

    def getSOParent(self):
        """
            get the strategic objective parent
        """
        return self.aq_inner.aq_parent.aq_inner.aq_parent

    def formatHealthIndicator(self):
        """
            Return the health indicator details with a specific html class following the health indicator field
        """
        return '<p class="fa-attr-valeur-%s">%s</p>' % (self.real_context.health_indicator.encode('utf8'),
                                                        self.display_text('health_indicator_details'))
