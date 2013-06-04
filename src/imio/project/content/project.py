from zope import schema
from zope.interface import implements
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.dexterity.schema import DexteritySchemaPolicy
from collective.task.content.task import ITask
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from imio.project import _


class IResultIndicatorSchema(Interface):
    """Schema used for the datagrid field 'result_indicator' of IProject."""
    label = schema.TextLine(
        title=_("Label"),
        required=True,)
    value = schema.TextLine(
        title=_("Value"),
        required=True,)


class IProject(ITask):
    """
        Project schema, field ordering
    """

    category = schema.List(
        title=_(u'Category'),
        value_type=schema.Choice(
            vocabulary=u'imio.project.content.project.category_vocabulary'
        )
    )
    result_indicator = schema.List(
        title=_(u'Result indicator'),
        value_type=DictRow(title=_("Result indicator"),
                           schema=IResultIndicatorSchema,
                           required=False),
    )
    directives.widget(result_indicator=DataGridFieldFactory)

    # remove title coming from ITask as we add it using the dublincore behavior
    directives.omitted('title')


class Project(Container):
    """ """
    implements(IProject)
    __ac_local_roles_block__ = False


class category_vocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        terms = []
        terms.append(SimpleTerm(u'Category 1', u'cat1', u'Category 1'))
        return SimpleVocabulary(terms)
category_vocabularyFactory = category_vocabulary()


class ProjectSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IProject, )
