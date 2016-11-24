# -*- coding: utf-8 -*-

from zope.annotation import IAnnotations

from collective.documentgenerator.helper.dexterity import DXDocumentGenerationHelperView
from collective.documentgenerator.helper.archetypes import ATDocumentGenerationHelperView
from imio.dashboard.browser.overrides import IDDocumentGenerationView
from imio.project.core.config import CHILDREN_BUDGET_INFOS_ANNOTATION_KEY
from imio.pyutils.bs import remove_attributes, replace_entire_strings, unwrap_tags

from views import _getWorkflowStates


class DocumentGenerationBaseHelper():
    """
        Common methods
    """

    objs = []
    sel_type = ''

    def is_dashboard(self):
        return 'facetedQuery' in self.request.form

    def uids_to_objs(self, brains):
        # can be used like this in normal template:
        # do section- if view.is_dashboard()
        # do text if view.uids_to_objs(brains)
        self.objs = []
        for brain in brains:
            self.objs.append(brain.getObject())
        self.sel_type = len(brains) and self.objs[0].portal_type or ''
        return False

    def context_var(self, name, default=''):
        """ Return context_variable value if defined or return default """
        ctx = self.appy_renderer.contentParser.env.context
        if name in ctx:
            return ctx['name']
        else:
            return default


class DocumentGenerationPSTHelper(DXDocumentGenerationHelperView, DocumentGenerationBaseHelper):
    """
        Methods used in document generation view, for pst
    """

    def getStrategicObjectives(self):
        """
            get a list of contained strategic objectives
        """
        if self.sel_type == 'strategicobjective':
            return self.objs
        else:
            pcat = self.real_context.portal_catalog
            brains = pcat(portal_type='strategicobjective',
                          path={'query': '/'.join(self.real_context.getPhysicalPath()), 'depth': 1},
                          review_state=_getWorkflowStates(self.portal, 'strategicobjective', skip_initial=True),
                          sort_on='getObjPositionInParent')
            return [brain.getObject() for brain in brains]

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

    def getTasks(self, action=None, depth=99):
        """
            Get tasks ordered by path
        """
        return self.getDGHV(action).getTasks(depth=depth)


class BudgetHelper():
    """
        Budget helper methods
    """
    def getOwnBudget(self):
        """
            get the own rendered widget
        """
        soup = self.display_widget('budget', soup=True)
        table = soup.find('fieldset').find('table')
        remove_attributes(table, ['class', 'id', 'data-id_prefix', 'data-name_prefix'])
        replace_entire_strings(table)
        unwrap_tags(table, ['span'])
        return str(table)

    def getChildrenBudget(self):
        """
            get the children budget
        """
        soup = self.display_widget('budget', soup=True)
        table = soup.find('table', class_='budgetinfos_table')
        remove_attributes(table, ['class', 'id'])
        replace_entire_strings(table)
        return str(table)

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


class DocumentGenerationSOHelper(DXDocumentGenerationHelperView, DocumentGenerationBaseHelper, BudgetHelper):
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
        if self.sel_type == 'operationalobjective':
            return self.objs
        else:
            context = so is None and self.real_context or so
            pcat = self.real_context.portal_catalog
            brains = pcat(portal_type='operationalobjective',
                          path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                          review_state=_getWorkflowStates(self.portal, 'operationalobjective', skip_initial=True),
                          sort_on='getObjPositionInParent')
            return [brain.getObject() for brain in brains]

    def getActions(self, oo=None):
        """
            return a list of contained pstactions
        """
        acts = self.getDGHV(oo).getActions()
        return acts

    def getTasks(self, action=None, depth=99):
        """
            Get tasks ordered by path
        """
        return self.getDGHV(action).getTasks(depth=depth)

    def getSection(self):
        """
            get the first part of a category value
        """
        try:
            return self.display_voc('categories').split(' - ')[0]
        except IndexError:  # pragma: no cover
            return ''

    def getDomain(self):
        """
            get the second part of a category value
        """
        try:
            return self.display_voc('categories').split(' - ')[1]
        except IndexError:  # pragma: no cover
            return ''


class DocumentGenerationOOHelper(DXDocumentGenerationHelperView, DocumentGenerationBaseHelper, BudgetHelper):
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
        if self.sel_type == 'pstaction':
            return self.objs
        else:
            context = oo is None and self.real_context or oo
            pcat = self.real_context.portal_catalog
            brains = pcat(portal_type='pstaction',
                          path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                          review_state=_getWorkflowStates(self.portal, 'pstaction', skip_initial=True),
                          sort_on='getObjPositionInParent')
            return [brain.getObject() for brain in brains]

    def getTasks(self, action=None, depth=99):
        """
            Get tasks ordered by path
        """
        return self.getDGHV(action).getTasks(depth=depth)

    def formatResultIndicator(self, expected=True, sep='<br />'):
        """
            return the result indicator as a string
        """
        rows = []
        for row in self.real_context.result_indicator:
            rows.append("%s = %d" % (row['label'].encode('utf8'), expected and row['value'] or row['reached_value']))
        return sep.join(rows)


class DocumentGenerationPSTActionsHelper(DXDocumentGenerationHelperView, DocumentGenerationBaseHelper, BudgetHelper):
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
        return self.real_context.aq_inner.aq_parent.aq_inner.aq_parent

    def formatHealthIndicator(self):
        """
            Return the health indicator details with a specific html class following the health indicator field
        """
        return '<p class="Santé-%s">%s</p>' % (self.real_context.health_indicator.encode('utf8'),
                                                self.display_text('health_indicator_details'))

    def getTasks(self, action=None, depth=99):
        """
            Get tasks ordered by path
        """
        pcat = self.real_context.portal_catalog
        brains = list(pcat(portal_type='task',
                           path={'query': '/'.join(self.real_context.getPhysicalPath()), 'depth': depth},
                           review_state=_getWorkflowStates(self.portal, 'task', skip_initial=True),
                           sort_on='path'))
        if depth > 1 and brains:
            brains.pop(0)
        return [brain.getObject() for brain in brains]


class DocumentGenerationPSTCategoriesHelper(ATDocumentGenerationHelperView, DocumentGenerationBaseHelper):
    """
        Helper for categories folder
    """


class CategoriesDocumentGenerationView(IDDocumentGenerationView):
    """
        Change context for folder categories => dashboard collections context
    """

    def _get_generation_context(self, helper_view, pod_template):
        """ """
        gen_context = super(CategoriesDocumentGenerationView, self)._get_generation_context(helper_view, pod_template)
        if hasattr(helper_view, 'uids_to_objs'):
            helper_view.uids_to_objs(gen_context.get('brains', []))
            if helper_view.sel_type:
                gen_context['context'] = helper_view.objs[0].aq_parent
                gen_context['view'] = helper_view.getDGHV(gen_context['context'])
        return gen_context
