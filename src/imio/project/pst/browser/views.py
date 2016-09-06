from zope.annotation import IAnnotations
from zope.component import getMultiAdapter, getUtility
from zope.component.interfaces import ComponentLookupError
from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory
from plone.app.textfield import RichTextValue
from plone.memoize import forever
from bs4 import BeautifulSoup as Soup
from imio.project.core.config import CHILDREN_BUDGET_INFOS_ANNOTATION_KEY


@forever.memoize
def _getWorkflowStates(portal, portal_type, skip_initial=False, skip_states=[]):
    """
        Return a list of a portal_type workflow states
    """
    pwkf = portal.portal_workflow
    ret = []
    workflows = pwkf.getChainForPortalType(portal_type)
    if not workflows:
        return ret
    workflow = pwkf[workflows[0]]
    for state in workflow.states:
        if skip_initial and state == workflow.initial_state:
            continue
        if skip_states and state in skip_states:
            continue
        ret.append(state)
    return ret


class DocumentGenerationMethods(object):
    """
        Common methods used in document generation view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.plone_view = getMultiAdapter((self.context, self.request), name=u'plone')
        self.plone_portal_state_view = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = self.plone_portal_state_view.portal()

    def __call__(self):
        return None

    def getParent(self):
        """
            get the parent object
        """
        return self.context.aq_inner.aq_parent

    def textFieldToHtml(self, fieldname, obj=None):
        """
            transform text field in html format
        """
        #return self.get(fieldname, obj=obj).replace('\r\n', '<br />')
        return self.portal.portal_transforms.convert('text_to_html', self.get(fieldname, obj=obj)).getData()

    def get(self, fieldname, obj=None, default=''):
        """
            get an attr and encode it if necessary.
            if attr is None, return default
        """
        if obj:
            the_obj = obj
        else:
            the_obj = self.context
        value = getattr(the_obj, fieldname)
        if value is None:
            return default
        if isinstance(value, RichTextValue):
            value = value.output
        if isinstance(value, unicode):
            value = value.encode('utf8')
        return value

    def widget(self, fieldname, obj=None, clean=False, soup=False):
        """
            get the rendered widget
        """
        if not obj:
            obj = self.context
        obj_view = getMultiAdapter((obj, obj.REQUEST), name=u'view')
        obj_view.updateFieldsFromSchemata()
        for field in obj_view.fields:
            if field != fieldname:
                obj_view.fields = obj_view.fields.omit(field)
        obj_view.updateWidgets()
        widget = obj_view.widgets[fieldname]
        rendered = widget.render()  # unicode
        if clean or soup:
            souped = Soup(rendered, "html.parser")
            if clean:
                for tag in souped.find_all(class_='required'):
                    tag.extract()
                for tag in souped.find_all(type='hidden'):
                    tag.extract()
            if soup:
                return souped
            else:
                return str(souped)  # is utf8
        else:
            return rendered.encode('utf8')

    def vocValue(self, vocabulary, fieldname, obj=None):
        """
            get the title of a vocabulary value
        """
        if obj:
            the_obj = obj
        else:
            the_obj = self.context
        factory = getUtility(IVocabularyFactory, vocabulary)
        voc = factory(the_obj)
        try:
            value = voc.getTerm(self.get(fieldname, obj=the_obj)).title
        except LookupError:
            value = translate('Missing: ${value}', domain='z3c.form',
                              mapping={'value': self.get(fieldname, obj=the_obj)}, context=self.request)
        if isinstance(value, unicode):
            value = value.encode('utf8')
        return value

    def vocValues(self, vocabulary, fieldname, obj=None, sep=None):
        """
            get the titles of a list vocabulary values
        """
        if obj:
            the_obj = obj
        else:
            the_obj = self.context
        factory = getUtility(IVocabularyFactory, vocabulary)
        voc = factory(the_obj)
        values = []
        for token in self.get(fieldname, obj=the_obj, default=[]):
            try:
                value = voc.getTerm(token).title
            except LookupError:
                value = translate('Missing: ${value}', domain='z3c.form',
                                  mapping={'value': self.get(fieldname, obj=the_obj)}, context=self.request)
            if isinstance(value, unicode):
                value = value.encode('utf8')
            values.append(value)
        if sep:
            return sep.join(values)
        return values

    def getState(self, obj=None, wf_id=None):
        """
            get the workflow state
        """
        if obj:
            the_obj = obj
        else:
            the_obj = self.context
        return self.context.portal_workflow.getInfoFor(the_obj, 'review_state', wf_id=wf_id)

    def getObjectDGM(self, obj):
        """
            get the object 'document-generation-methods' view
        """
        try:
            return getMultiAdapter((obj, self.request), name=u'document-generation-methods')
        except ComponentLookupError:
            return None


class DocumentGenerationPSTMethods(DocumentGenerationMethods):
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
        oos = self.getObjectDGM(so).getOperationalObjectives()
        return oos

    def getActions(self, oo=None):
        """
            return a list of contained pstactions
        """
        acts = self.getObjectDGM(oo).getActions()
        return acts


class DocumentGenerationSOMethods(DocumentGenerationMethods):
    """
        Methods used in document generation view, for strategicobjective
    """

    def getStrategicObjectives(self):
        """
            get a list of unique contained strategic objective
        """
        return [self.context]

    def getOperationalObjectives(self, obj=None):
        """
            get a list of contained operational objectives
        """
        pcat = self.context.portal_catalog
        brains = pcat(portal_type='operationalobjective',
                      path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
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
        acts = self.getObjectDGM(oo).getActions()
        return acts

    def getSection(self):
        """
            get the first part of a category value
        """
        try:
            return self.vocValue(u'imio.project.core.content.project.categories_vocabulary',
                                 'categories').split(' - ')[0]
        except IndexError:
            return ''

    def getDomain(self):
        """
            get the second part of a category value
        """
        try:
            return self.vocValue(u'imio.project.core.content.project.categories_vocabulary',
                                 'categories').split(' - ')[1]
        except IndexError:
            return ''

    def getOwnBudget(self, obj=None):
        """
            get the own rendered widget
        """
        soup = self.widget('budget', obj=obj, clean=True, soup=True)
        return str(soup.find('fieldset').find('table'))

    def getChildrenBudget(self, obj=None):
        """
            get the children budget
        """
        soup = self.widget('budget', obj, clean=True, soup=True)
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


class DocumentGenerationOOMethods(DocumentGenerationMethods):
    """
        Methods used in document generation view, for operationalobjective
    """

    def getStrategicObjectives(self):
        """
            get a list of the parent strategic objective of the current operationalobjective
        """
        return [self.context.aq_inner.aq_parent]

    def getOperationalObjectives(self, obj=None):
        """
            get a list of an unique contained operational objective
        """
        return [self.context]

    def formatResultIndicator(self, expected=True, sep='<br />'):
        """
            return the result indicator as a string
        """
        rows = []
        for row in self.context.result_indicator:
            rows.append("%s = %d" % (row['label'].encode('utf8'), expected and row['value'] or row['reached_value']))
        return sep.join(rows)

    def getActions(self, oo=None):
        """
            return a list of contained pstactions
        """
        pcat = self.context.portal_catalog
        brains = pcat(portal_type='pstaction',
                      path={'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
                      review_state=_getWorkflowStates(self.portal, 'pstaction', skip_initial=True),
                      sort_on='getObjPositionInParent')
        return [brain.getObject() for brain in brains]


class DocumentGenerationPSTActionMethods(DocumentGenerationMethods):
    """
        Methods used in document generation view, for PSTAction
    """

    def getStrategicObjectives(self):
        """
            get a list of the parent strategic objective of the current operationalobjective
        """
        return [self.context.aq_inner.aq_parent.aq_inner.aq_parent]

    def getOperationalObjectives(self, obj=None):
        """
            get a list of an unique contained operational objective
        """
        return [self.context.aq_inner.aq_parent]

    def getSOParent(self):
        """
            get the strategic objective parent
        """
        return self.getParent().aq_inner.aq_parent

    def formatHealthIndicator(self):
        """
            Return the health indicator details with a specific html class following the health indicator field
        """
        return '<p class="fa-attr-valeur-%s">%s</p>' % (self.context.health_indicator.encode('utf8'),
                                                        self.get('health_indicator_details').replace('\r\n', '<br />'))

    def getActions(self, oo=None):
        """
            return a list of contained pstactions
        """
        return [self.context]
