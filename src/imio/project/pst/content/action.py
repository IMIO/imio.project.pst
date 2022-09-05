# -*- coding: utf-8 -*-
from zc.relation.interfaces import ICatalog

from Acquisition import aq_inner
from collective.contact.plonegroup.utils import organizations_with_suffixes
from collective.task.interfaces import ITaskContent
from collective.z3cform.chosen.widget import AjaxChosenFieldWidget
from collective.z3cform.chosen.widget import AjaxChosenMultiFieldWidget
from collective.z3cform.datagridfield import DataGridFieldFactory
# from dexterity.localrolesfield.field import LocalRoleField
from collective.z3cform.datagridfield import DictRow
from dexterity.localrolesfield.field import LocalRolesField
from imio.helpers.content import get_from_annotation
from imio.project.core.browser.views import ProjectAddForm
from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project
from imio.project.core.utils import getProjectSpace
from imio.project.pst import _
from imio.project.pst.utils import find_max_deadline_on_children
from plone import api
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.schema import DexteritySchemaPolicy
from plone.directives.form import default_value
from z3c.form import validator
from z3c.form.datamanager import AttributeField
from z3c.form.interfaces import IDataManager
from zope import schema
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import implementer
from zope.interface import implements
from zope.interface import invariant
from zope.interface import provider
from zope.intid.interfaces import IIntIds
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.security import checkPermission
from zope.security.interfaces import NoInteraction


@provider(IFormFieldProvider)
class IBudgetSplitSchema(Interface):
    """"""

    uid = schema.TextLine(
        title=_(u"UID"),
        required=True,
    )

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    percentage = schema.Float(
        title=_(u"Percentage"),
        required=True,
        min=0.0,
        max=100.0,
    )


class IPSTAction(IProject):
    """
        PSTAction schema, field ordering
    """

    representative_responsible = LocalRolesField(
        title=_(u"Representative responsible"),
        description=_(u"Choose principals that will be representative responsible for this project. "
                      u"If nothing choosed, the oo value is used for searches."),
        value_type=schema.Choice(
            vocabulary=u'imio.project.core.content.project.manager_vocabulary',
        ),
        required=False,
    )
    form.widget('representative_responsible', AjaxChosenMultiFieldWidget, populate_select=True)

    responsible = schema.Choice(
        title=_(u'Responsible'),
        vocabulary=u'imio.project.pst.ActionEditorsVocabulary',
        required=False,
    )
    form.widget('responsible', AjaxChosenFieldWidget, populate_select=True)

    health_indicator = schema.Choice(
        title=_(u'Health indicator'),
        # description=_(u"Choose a health level."),
        vocabulary=u'imio.project.pst.content.action.health_indicator_vocabulary',
    )

    health_indicator_details = schema.Text(
        title=_(u'Health indicator_details'),
        # description=_(u"Details concerning the action health."),
        required=False,
    )

    # change label
    form.widget('result_indicator', DataGridFieldFactory, display_table_css_class='listing nosort',
                label=_(u'Realisation indicator'))

    budget_split = schema.List(
        title=_(u"Budget split"),
        required=False,
        value_type=DictRow(
            title=_("Budget split"), schema=IBudgetSplitSchema, required=False
        ),
    )

    @invariant
    def budget_split_total_invariant(data):
        budget_split = getattr(data, 'budget_split', [])
        if budget_split and sum([line.get('percentage') for line in budget_split]) != 100.0:
            raise Invalid(_(u'The sum of all percentages must amount to 100 %.'))


# We add a default value for the pstaction. This works but changes on other field params don't work.
# IPSTAction['manager'].defaultFactory = default_manager

@default_value(field=IPSTAction['manager'])
def default_manager(data):
    if not data.context.portal_type == 'operationalobjective':
        return []
    member_groups = api.group.get_groups(user=api.user.get_current())
    orgs = organizations_with_suffixes(member_groups, ['actioneditor'])
    return [org for org in data.context.manager if org in orgs]


class ManagerFieldValidator(validator.SimpleFieldValidator):
    def validate(self, value):
        # we call the already defined validators
        super(ManagerFieldValidator, self).validate(value)
        member = api.user.get_current()
        # bypass for Managers
        if member.has_role('Manager'):
            return True

        # if not value:  # covered by min_length
        #     raise Invalid(_(u"You must choose at least one group"))

        member_groups = api.group.get_groups(user=member)
        member_groups_ids = [g.id for g in member_groups]
        if 'pst_editors' in member_groups_ids:
            return True

        member_orgs = organizations_with_suffixes(member_groups, ['actioneditor'])

        # if not Manager, check if the user selected at least one of the groups
        # he is member of or he will not be able to see the element after saving

        def check_intersection():
            for org in value:
                if org in member_orgs:
                    return True
            return False

        if not check_intersection():
            raise Invalid(_(u"You must choose at least one group of which you are a member"))


# validator.WidgetValidatorDiscriminators(ManagerFieldValidator, field=IPSTAction['manager'])
# provideAdapter(ManagerFieldValidator)


class PSTAction(Project):
    """ """
    implements(IPSTAction)
    # we block local roles acquisition
    __ac_local_roles_block__ = True

    def Title(self):
        if getattr(getProjectSpace(self), 'use_ref_number', True):
            return '%s (A.%s)' % (self.title.encode('utf8'), self.reference_number)
        else:
            return '%s (A)' % (self.title.encode('utf8'))

    def back_references(self):
        """
        Return back references from source object on specified attribute_name
        """
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = []
        to_id = intids.queryId(aq_inner(self))
        if not to_id:
            return result
        for rel in catalog.findRelations(
                dict(to_id=to_id,
                     from_attribute='symbolic_link')
        ):
            if not rel.from_object:
                continue
            obj = intids.queryObject(rel.from_id)
            if obj is not None and checkPermission('zope2.View', obj):
                result.append(obj)
        return result

    def allowedContentTypes(self):
        allowed = super(PSTAction, self).allowedContentTypes()
        for item in self.listFolderContents():
            if IPSTSubAction.providedBy(item):
                allowed = [fti for fti in allowed if fti.id != 'task']
                break
            if ITaskContent.providedBy(item):
                allowed = [fti for fti in allowed if fti.id != 'subaction_link']
                break
        return allowed

    def has_subactions(self):
        return get_from_annotation('imio.project.pst.has_subactions', obj=self, default=False)


@implementer(IDataManager)
class PSTActionDataManager(AttributeField):
    def get(self):
        value = super(PSTActionDataManager, self).get()
        if self.field.__name__ == "planned_end_date":
            value = self.context.planned_end_date
            if not value:
                value = find_max_deadline_on_children(
                    self.context,
                    {
                        "pstsubaction": "planned_end_date",
                        "subaction_link": "planned_end_date",
                        "task": "due_date"
                    }
                )
        return value


class PSTActionSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IPSTAction,)


class HealthIndicatorVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        terms = []
        terms.append(SimpleTerm(u'bon', u'bon', u'Bon'))
        terms.append(SimpleTerm(u'risque', u'risque', u'Risque'))
        terms.append(SimpleTerm(u'blocage', u'blocage', u'Blocage'))
        terms.append(SimpleTerm(u'pause', u'pause', u'En pause'))
        return SimpleVocabulary(terms)


class ActionAddForm(ProjectAddForm):
    portal_type = 'pstaction'


class ActionAdd(DefaultAddView):
    form = ActionAddForm


class IPSTSubAction(IPSTAction):
    pass


class PSTSubAction(Project):
    """ """
    implements(IPSTSubAction)
    # we block local roles acquisition
    __ac_local_roles_block__ = True

    def Title(self):
        if getattr(getProjectSpace(self), 'use_ref_number', True):
            return '%s (SA.%s)' % (self.title.encode('utf8'), self.reference_number)
        else:
            return '%s (SA)' % (self.title.encode('utf8'))

    def back_references(self):
        """
        Return back references from source object on specified attribute_name
        """
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = []
        to_id = intids.queryId(aq_inner(self))
        if not to_id:
            return result
        for rel in catalog.findRelations(
                dict(to_id=to_id,
                     from_attribute='symbolic_link')
        ):
            if not rel.from_object:
                continue
            obj = intids.queryObject(rel.from_id)
            # TODO : Fix NoInteraction exception
            try:
                if obj is not None and checkPermission('zope2.View', obj):
                    result.append(obj)
            except NoInteraction:
                pass
        return result

    def has_subactions(self):
        return False


@implementer(IDataManager)
class PSTSubActionDataManager(AttributeField):
    def get(self):
        value = super(PSTSubActionDataManager, self).get()
        if self.field.__name__ == "planned_end_date":
            value = self.context.planned_end_date
            if not value:
                value = find_max_deadline_on_children(self.context, {"task": "due_date"})
        return value


class SubActionAddForm(ProjectAddForm):
    portal_type = 'pstsubaction'


class SubActionAdd(DefaultAddView):
    form = SubActionAddForm
