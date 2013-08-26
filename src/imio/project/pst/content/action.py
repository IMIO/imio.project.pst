# -*- coding: utf-8 -*-

from zope.interface import implements
from zope import schema
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from plone.app.textfield import RichText
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

    health_indicator_details = schema.Text(
        title=_(u'Health indicator_details'),
        description=_(u"Details concerning the action health."),
        required=False,
    )

    work_plan = RichText(
        title=_(u"Work plan"),
        description=_("Enter work to do."),
        required=False,
        default_mime_type='text/html',
        output_mime_type='text/html',
        allowed_mime_types=('text/html',),
    )

    # reorder fields
    form.order_before(planned_end_date='comments')
    form.order_before(planned_begin_date='comments')
    form.order_before(effective_begin_date='comments')
    form.order_before(effective_end_date='comments')
    form.order_before(progress='comments')
    form.order_before(health_indicator='comments')
    form.order_before(health_indicator_details='comments')
    form.order_before(manager='comments')
    form.order_before(visible_for='comments')
    form.order_before(extra_concerned_people='comments')
    form.order_before(budget='comments')
    form.order_before(budget_comments='comments')
    form.order_before(work_plan='comments')
    form.order_before(observation='comments')

    # hide some fields
    form.omitted('categories')
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
        terms.append(SimpleTerm(u'bon', u'bon', u'Bon'))
        terms.append(SimpleTerm(u'risque', u'risque', u'Risque'))
        terms.append(SimpleTerm(u'blocage', u'blocage', u'Blocage'))
        return SimpleVocabulary(terms)
