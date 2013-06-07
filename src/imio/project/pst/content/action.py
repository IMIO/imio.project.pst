from zope.interface import implements
from zope import schema
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives as form
from plone.dexterity.schema import DexteritySchemaPolicy

from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project
from imio.project.pst import _


class IPSTAction(IProject):
    """
        PSTAction schema, field ordering
    """
    health_indicator = schema.Choice(
        title=_(u'Health indicator'),
        description=_(u"Choose a health level."),
        vocabulary=u'imio.project.pst.content.action.health_indicator_vocabulary',
    )

    work_plan = schema.Text(
        title=_(u"Work plan"),
        description=_("Enter work to do."),
        required=False,
    )
    form.widget(work_plan=WysiwygFieldWidget)

    # reorder new added fields
    form.order_before(health_indicator='comments')
    form.order_before(work_plan='comments')

    # hide some fields
    form.omitted('category')
    form.omitted('priority')
    form.omitted('result_indicator')


class PSTAction(Project):
    """ """
    implements(IPSTAction)


class PSTActionSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IPSTAction, )


class HealthIndicatorVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        terms = []
        terms.append(SimpleTerm(u'Bon', u'bon', u'Bon'))
        terms.append(SimpleTerm(u'Risque', u'risque', u'Risque'))
        terms.append(SimpleTerm(u'Blocage', u'blocage', u'Blocage'))
        return SimpleVocabulary(terms)
