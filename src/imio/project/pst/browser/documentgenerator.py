# -*- coding: utf-8 -*-

from collective.documentgenerator.helper.archetypes import ATDocumentGenerationHelperView
from collective.documentgenerator.helper.dexterity import DXDocumentGenerationHelperView
from collective.eeafaceted.dashboard.browser.overrides import DashboardDocumentGenerationView
from collective.symlink.utils import is_linked_object
from imio.project.core.config import CHILDREN_BUDGET_INFOS_ANNOTATION_KEY as CBIAK
from imio.project.core.utils import getProjectSpace
from imio.project.pst.utils import filter_states
from imio.pyutils.bs import remove_attributes
from imio.pyutils.bs import replace_entire_strings
from imio.pyutils.bs import unwrap_tags
from plone import api
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class DocumentGenerationBaseHelper():
    """
        Common methods
    """

    objs = []
    sel_type = ''
    activated_fields = {}

    def is_dashboard(self):
        """ Test if template is rendered from a dashboard """
        return 'facetedQuery' in self.request.form

    def uids_to_objs(self, brains):
        """ set objects from brains """
        # can be used like this in normal template:
        # do section- if view.is_dashboard()
        # do text if view.uids_to_objs(brains)
        self.objs = []
        for brain in brains:
            self.objs.append(brain.getObject())
        self.sel_type = len(brains) and self.objs[0].portal_type or ''
        return False

    def flatten_structure(self):
        """ Return tuples of flattened objects """
        if self.is_dashboard():
            brains = self.context_var('brains', default=None)
            if brains is not None:
                self.uids_to_objs(brains)
        ret = []
        for so in self.getStrategicObjectives(skip_states=[]):
            so_v = self.getDGHV(so)
            oos = self.getOperationalObjectives(so=so, skip_states=[])
            if not oos:
                ret.append((so_v, None, None))
                continue
            for oo in oos:
                oo_v = self.getDGHV(oo)
                acts = self.getActions(oo=oo, skip_states=[])
                if not acts:
                    ret.append((so_v, oo_v, None))
                    continue
                for act in acts:
                    act_v = self.getDGHV(act)
                    ret.append((so_v, oo_v, act_v))
        return ret

    def skip_states(self):
        return self.context_var('skip_states').split(',')

    def init_hv(self):
        """ init method to be called in document """
        def _get_fields(pt):
            return [fld.split('.')[-1] for fld in
                    api.portal.get_registry_record('imio.project.settings.{}_fields'.format(pt), default=[])]

        self.activated_fields = {
            'so': _get_fields('strategicobjective'),
            'oo': _get_fields('operationalobjective'),
            'ac': _get_fields('pstaction'),
            'sb': _get_fields('pstsubaction'),
        }

    def keep_field(self, key, field):
        return field in self.activated_fields[key]


class DocumentGenerationPSTHelper(DXDocumentGenerationHelperView, DocumentGenerationBaseHelper):
    """
        Methods used in document generation view, for pst
    """

    def getStrategicObjectives(self, skip_states=['created']):
        """
            get a list of contained strategic objectives
        """
        if self.is_dashboard() and self.sel_type == 'strategicobjective':
            return self.objs
        else:
            pcat = self.real_context.portal_catalog
            brains = pcat(portal_type='strategicobjective',
                          path={'query': '/'.join(self.real_context.getPhysicalPath()), 'depth': 1},
                          review_state=filter_states(self.portal, 'strategicobjective', skip_states),
                          sort_on='getObjPositionInParent')
            return [brain.getObject() for brain in brains]

    def getOperationalObjectives(self, so=None, skip_states=['created']):
        """
            get a list of contained operational objectives
        """
        oos = self.getDGHV(so).getOperationalObjectives(skip_states=skip_states)
        return oos

    def getActions(self, oo=None, skip_states=['created']):
        """
            return a list of contained pstactions
        """
        acts = self.getDGHV(oo).getActions(skip_states=skip_states)
        return acts

    def getSubActions(self, action=None, skip_states=['created']):
        """
            return a list of contained pstsubactions
        """
        subs = self.getDGHV(action).getSubActions(skip_states=skip_states)
        return subs

    def getTasks(self, action=None, depth=99, skip_states=['created']):
        """
            Get tasks ordered by path
        """
        return self.getDGHV(action).getTasks(depth=depth, skip_states=skip_states)


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

    def getOwnBudgetAsText(self):
        """
            get the own rendered widget
        """
        #[{'amount': 12500.0, 'budget_type': 'wallonie', 'year': 2017}, {'amount': 2500.0, 'budget_type': 'europe',
        #'year': 2017}, {'amount': 250.0, 'budget_type': 'federation-wallonie-bruxelles', 'year': 2017},
        #{'amount': 250.0, 'budget_type': 'province', 'year': 2017}]
        if not self.real_context.budget:
            return ''
        ret = []
        budget_types = {}
        factory = getUtility(IVocabularyFactory, 'imio.project.core.content.project.budget_type_vocabulary')
        voc = factory(self.real_context)
        for term in voc:
            budget_types[term.value] = term.title.encode('utf8')

        for dic in self.real_context.budget:
            ret.append("%d pour %s: %d€" % (dic['year'], budget_types.get(dic['budget_type'], dic['budget_type']),
                       dic['amount']))
        return ' | '.join(ret)

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
        if CBIAK in obj_annotations:
            for uid in obj_annotations[CBIAK]:
                if obj_annotations[CBIAK][uid]:
                    return True
        return False

    def getGlobalBudgetByYear(self):
        """
            Return a dictionary containing globalized budgets per year
        """
        # initialize the dictionary in the year range defined by the project space
        fixed_years = [y for y in getProjectSpace(self.real_context).budget_years or []]
        budget_by_year = {year: 0 for year in fixed_years}
        # get the persistent dict
        annotations = IAnnotations(self.real_context)
        # get the children budget amounts
        if CBIAK in annotations:
            globalised_budget = annotations[CBIAK]
            for child in globalised_budget:
                for budget in globalised_budget[child]:
                    if budget['year'] in fixed_years:
                        budget_by_year[budget['year']] += budget['amount']
        # get the current element budget amounts
        for budget in self.real_context.budget:
            if budget['year'] in fixed_years:
                budget_by_year[budget['year']] += budget['amount']
        return budget_by_year


class DocumentGenerationSOHelper(DXDocumentGenerationHelperView, DocumentGenerationBaseHelper, BudgetHelper):
    """
        Methods used in document generation view, for strategicobjective
    """

    def getStrategicObjectives(self, skip_states=['created']):
        """
            get a list of unique contained strategic objective
        """
        if self.is_dashboard() and self.sel_type == 'operationalobjective':
            ret = []
            for obj in self.objs:
                os = obj.__parent__
                if os not in ret:
                    ret.append(os)
            return ret
        else:
            return [self.real_context]

    def getOperationalObjectives(self, so=None, skip_states=['created']):
        """
            get a list of contained operational objectives
        """
        if self.is_dashboard() and self.sel_type == 'operationalobjective':
            return [oo for oo in self.objs if oo.__parent__ == so]
        else:
            context = so is None and self.real_context or so
            pcat = self.real_context.portal_catalog
            brains = pcat(portal_type='operationalobjective',
                          path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                          review_state=filter_states(self.portal, 'operationalobjective', skip_states),
                          sort_on='getObjPositionInParent')
            return [brain.getObject() for brain in brains]

    def getActions(self, oo=None, skip_states=['created']):
        """
            return a list of contained pstactions
        """
        acts = self.getDGHV(oo).getActions(skip_states=skip_states)
        return acts

    def getSubActions(self, action=None, skip_states=['created']):
        """
            return a list of contained pstsubactions
        """
        subs = self.getDGHV(action).getSubActions(skip_states=skip_states)
        return subs

    def getTasks(self, action=None, depth=99, skip_states=['created']):
        """
            Get tasks ordered by path
        """
        return self.getDGHV(action).getTasks(depth=depth, skip_states=skip_states)

    def getSection(self):
        """
            get the first part of a category value
        """
        for cat in self.display_voc('categories', separator='|').split('|'):
            if ' - ' in cat:
                return cat.split(' - ')[0]
        return ''

    def getDomain(self):
        """
            get the second part of a category value
        """
        for cat in self.display_voc('categories', separator='|').split('|'):
            if ' - ' in cat:
                return cat.split(' - ')[1]
        return ''


class DocumentGenerationOOHelper(DXDocumentGenerationHelperView, DocumentGenerationBaseHelper, BudgetHelper):
    """
        Methods used in document generation view, for operationalobjective
    """

    def getStrategicObjectives(self, skip_states=['created']):
        """
            get a list of the parent strategic objective of the current operationalobjective
        """
        if self.is_dashboard() and self.sel_type == 'pstaction':
            ret = []
            for obj in self.objs:
                os = obj.__parent__.__parent__
                if os not in ret:
                    ret.append(os)
            return ret
        else:
            return [self.real_context.aq_inner.aq_parent]

    def getOperationalObjectives(self, so=None, skip_states=['created']):
        """
            get a list of an unique contained operational objective
        """
        if self.is_dashboard() and self.sel_type == 'pstaction':
            ret = []
            for obj in self.objs:
                oo = obj.__parent__
                if oo.__parent__ != so:
                    continue
                if oo not in ret:
                    ret.append(oo)
            return ret
        else:
            return [self.real_context]

    def getActions(self, oo=None, skip_states=['created']):
        """
            return a list of contained pstactions
        """
        if self.is_dashboard() and self.sel_type == 'pstaction':
            return [act for act in self.objs if act.__parent__ == oo]
        else:
            context = oo is None and self.real_context or oo
            pcat = self.real_context.portal_catalog
            brains = pcat(portal_type='pstaction',
                          path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                          review_state=filter_states(self.portal, 'pstaction', skip_states),
                          sort_on='getObjPositionInParent')
            return [brain.getObject() for brain in brains]

    def getSubActions(self, action=None, skip_states=['created']):
        """
            return a list of contained pstsubactions
        """
        subs = self.getDGHV(action).getSubActions(skip_states=skip_states)
        return subs

    def getTasks(self, action=None, depth=99, skip_states=['created']):
        """
            Get tasks ordered by path
        """
        return self.getDGHV(action).getTasks(depth=depth, skip_states=skip_states)

    def formatResultIndicator(self, reached=True, expected=True, sep=' | '):
        """
            return the result indicator as a string
        """
        rows = []
        for row in self.real_context.result_indicator:
            if reached and expected:
                rows.append("%s = %d / %d" % (row['label'].encode('utf8'), row['reached_value'], row['value']))
            elif reached:
                rows.append("%s = %d" % (row['label'].encode('utf8'), row['reached_value']))
            elif expected:
                rows.append("%s = %d" % (row['label'].encode('utf8'), row['value']))
        return sep.join(rows)


class DocumentGenerationPSTActionsHelper(DXDocumentGenerationHelperView, DocumentGenerationBaseHelper, BudgetHelper):
    """
        Methods used in document generation view, for PSTAction
    """

    def is_linked(self):
        return is_linked_object(self.real_context)

    def getStrategicObjectives(self, skip_states=['created']):
        """
            get a list of the parent strategic objective of the current operationalobjective
        """
        if self.is_dashboard() and self.sel_type in ('task', 'pstsubaction'):
            ret = []
            for obj in self.objs:
                os = obj.__parent__.__parent__.__parent__
                if os not in ret:
                    ret.append(os)
            return ret
        else:
            return [self.real_context.aq_inner.aq_parent.aq_inner.aq_parent]

    def getOperationalObjectives(self, so=None, skip_states=['created']):
        """
            get a list of an unique contained operational objective
        """
        if self.is_dashboard() and self.sel_type in ('task', 'pstsubaction'):
            ret = []
            for obj in self.objs:
                oo = obj.__parent__.__parent__
                if oo.__parent__ != so:
                    continue
                if oo not in ret:
                    ret.append(oo)
            return ret
        else:
            return [self.real_context.aq_inner.aq_parent]

    def getActions(self, oo=None, skip_states=['created']):
        """
            return a list of contained pstactions
        """
        if self.is_dashboard() and self.sel_type in ('task', 'pstsubaction'):
            ret = []
            for obj in self.objs:
                act = obj.__parent__
                if act.__parent__ != oo:
                    continue
                if act not in ret:
                    ret.append(act)
            return ret
        else:
            return [self.real_context]

    def getSubActions(self, action=None, skip_states=['created']):
        """
            return a list of contained pstsubactions
        """
        if self.is_dashboard() and self.sel_type == 'pstsubaction':
            return [act for act in self.objs if act.__parent__ == action]
        elif self.is_dashboard() and self.sel_type == 'task':
            return []
        else:
            context = action is None and self.real_context or action
            pcat = self.real_context.portal_catalog
            brains = pcat(portal_type='pstsubaction',
                          path={'query': '/'.join(context.getPhysicalPath()), 'depth': 1},
                          review_state=filter_states(self.portal, 'pstsubaction', skip_states),
                          sort_on='getObjPositionInParent')
            return [brain.getObject() for brain in brains]

    def formatHealthIndicator(self):
        """
            Return the health indicator details with a specific html class following the health indicator field
        """
        return '<p class="Santé-%s">%s</p>' % (self.real_context.health_indicator.encode('utf8'),
                                                self.display_text_as_html('health_indicator_details'))

    def formatResultIndicator(self, reached=True, expected=True, sep=' | '):
        """
            Return the result indicator as a string
        """
        rows = []
        for row in (self.real_context.result_indicator or []):
            if reached and expected:
                rows.append("%s = %d / %d" % (row['label'].encode('utf8'), row['reached_value'], row['value']))
            elif reached:
                rows.append("%s = %d" % (row['label'].encode('utf8'), row['reached_value']))
            elif expected:
                rows.append("%s = %d" % (row['label'].encode('utf8'), row['value']))
        return sep.join(rows)

    def getTasks(self, action=None, depth=99, skip_states=['created']):
        """
            Get tasks ordered by path
        """
        if self.is_dashboard() and self.sel_type == 'task':
            return [tsk for tsk in self.objs if tsk.__parent__ == action]
        if self.is_dashboard() and self.sel_type == 'pstsubaction':
            return []
        else:
            context = action is None and self.real_context or action
            pcat = self.real_context.portal_catalog
            brains = pcat(portal_type='task',
                          path={'query': '/'.join(context.getPhysicalPath()), 'depth': depth},
                          review_state=filter_states(self.portal, 'task', skip_states),
                          sort_on='path')
            return [brain.getObject() for brain in brains]


class DocumentGenerationPSTSubActionsHelper(DocumentGenerationPSTActionsHelper):
    """
        Methods used in document generation view, for PSTSubAction
    """

    def getStrategicObjectives(self, skip_states=['created']):
        """
            get a list of the parent strategic objective of the current operationalobjective
        """
        if self.is_dashboard() and self.sel_type == 'task':
            ret = []
            for obj in self.objs:
                os = obj.__parent__.__parent__.__parent__.__parent__
                if os not in ret:
                    ret.append(os)
            return ret
        else:
            return [self.real_context.aq_inner.aq_parent.aq_inner.aq_parent.aq_inner.aq_parent]

    def getOperationalObjectives(self, so=None, skip_states=['created']):
        """
            get a list of an unique contained operational objective
        """
        if self.is_dashboard() and self.sel_type == 'task':
            ret = []
            for obj in self.objs:
                oo = obj.__parent__.__parent__.__parent__
                if oo.__parent__ != so:
                    continue
                if oo not in ret:
                    ret.append(oo)
            return ret
        else:
            return [self.real_context.aq_inner.aq_parent.aq_inner.aq_parent]

    def getActions(self, oo=None, skip_states=['created']):
        """
            return a list of contained pstactions
        """
        if self.is_dashboard() and self.sel_type == 'task':
            ret = []
            for obj in self.objs:
                act = obj.__parent__.__parent__
                if act.__parent__ != oo:
                    continue
                if act not in ret:
                    ret.append(act)
            return ret
        else:
            return [self.real_context.aq_inner.aq_parent]

    def getSubActions(self, action=None, skip_states=['created']):
        """
            return a list of contained pstsubactions
        """
        if self.is_dashboard() and self.sel_type == 'task':
            ret = []
            for obj in self.objs:
                sub = obj.__parent__
                if sub.__parent__ != action:
                    continue
                if sub not in ret:
                    ret.append(sub)
            return ret
        else:
            return [self.real_context]

    def getTasks(self, action=None, depth=99, skip_states=['created']):
        """
            Get tasks ordered by path
        """
        if self.is_dashboard() and self.sel_type == 'task':
            return [tsk for tsk in self.objs if tsk.__parent__ == action]
        else:
            context = action is None and self.real_context or action
            pcat = self.real_context.portal_catalog
            brains = pcat(portal_type='task',
                          path={'query': '/'.join(context.getPhysicalPath()), 'depth': depth},
                          review_state=filter_states(self.portal, 'task', skip_states),
                          sort_on='path')
            return [brain.getObject() for brain in brains]


class DocumentGenerationPSTCategoriesHelper(ATDocumentGenerationHelperView, DocumentGenerationBaseHelper):
    """
        Helper for categories folder
    """


class CategoriesDocumentGenerationView(DashboardDocumentGenerationView):
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
