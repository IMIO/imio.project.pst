import datetime
from zope import schema
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.dexterity.schema import DexteritySchemaPolicy
from plone.formwidget.datetime.z3cform.widget import DateFieldWidget
from collective.task.content.task import ITask
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from collective.z3cform.rolefield.field import LocalRolesToPrincipals
from imio.project import _


class IResultIndicatorSchema(Interface):
    """Schema used for the datagrid field 'result_indicator' of IProject."""
    label = schema.TextLine(
        title=_("Label"),
        required=True,)
    value = schema.Int(
        title=_("Value"),
        required=True,)


class IProject(ITask):
    """
        Project schema, field ordering
    """

    category = schema.List(
        title=_(u'Category'),
        description=_(u"Choose a category."),
        value_type=schema.Choice(
            vocabulary=u'imio.project.content.project.category_vocabulary',
        )
    )
    result_indicator = schema.List(
        title=_(u'Result indicator'),
        description=_(u"Enter one indicator by row. Value is a number. "
                      "Label must precise the signification of this number."),
        value_type=DictRow(title=_("Result indicator"),
                           schema=IResultIndicatorSchema,
                           required=False),
    )
    directives.widget(result_indicator=DataGridFieldFactory)

    priority = schema.Choice(
        title=_(u'Priority'),
        description=_(u"Choose a priority."),
        vocabulary=u'imio.project.content.project.priority_vocabulary',
    )

    visible_for = LocalRolesToPrincipals(
        title=_(u"Visible for"),
        description=_(u"Choose principals that can see this project."),
        required=False,
        roles_to_assign=('Reader',),
        value_type=schema.Choice(
            vocabulary=u'plone.principalsource.Principals'
        )
    )

    budget = schema.Text(
        title=_(u"Budget"),
        description=_("Budget details"),
    )

    planned_begin_date = schema.Date(
        title=_(u'Planned begin date'),
        description=_(u"Enter a planned date for the beginning."),
        required=False,
        defaultFactory=datetime.date.today,
    )
    directives.widget(planned_begin_date=DateFieldWidget)

    # remove title coming from ITask as we add it using the dublincore behavior
    directives.omitted('title')


class Project(Container):
    """ """
    implements(IProject)
    __ac_local_roles_block__ = False
    import ipdb; ipdb.set_trace()
    from z3c.form import field
    fields = field.Fields(IProject)
#    fields['deadline'].widget.show_time = False


class CategoryVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        terms = []
        terms.append(SimpleTerm(u'Category 1', u'cat1', u'Category 1'))
        return SimpleVocabulary(terms)
category_vocabulary_factory = CategoryVocabulary()


class PriorityVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        terms = []
        terms.append(SimpleTerm(u'Low', u'low', u'Low'))
        terms.append(SimpleTerm(u'Normal', u'normal', u'Normal'))
        terms.append(SimpleTerm(u'High', u'high', u'High'))
        return SimpleVocabulary(terms)
priority_vocabulary_factory = PriorityVocabulary()


class ProjectSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IProject, )
