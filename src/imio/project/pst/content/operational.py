# -*- coding: utf-8 -*-

from zope.interface import implements
from zope import schema
from zope.schema.interfaces import IVocabularyFactory

from plone.autoform import directives as form
from plone.dexterity.schema import DexteritySchemaPolicy

from collective.z3cform.rolefield.field import LocalRolesToPrincipals

from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project
from imio.project.core.utils import getVocabularyTermsForOrganization
from imio.project.pst import _


class IOperationalObjective(IProject):
    """
        OperationalObjective schema, field ordering
    """
    representative_responsible = LocalRolesToPrincipals(
        title=_(u"Representative responsible"),
        description=_(u"Choose principals that will be representative responsible for this project."),
        roles_to_assign=('Editor',),
        value_type=schema.Choice(
            vocabulary=u'imio.project.pst.content.operational.representative_responsible_vocabulary',
        ),
        required=True,
    )

    administrative_responsible = LocalRolesToPrincipals(
        title=_(u"Administrative responsible"),
        description=_(u"Choose principals that will be administrative responsible for this project."),
        roles_to_assign=('Editor',),
        value_type=schema.Choice(
            vocabulary=u'imio.project.pst.content.operational.administrative_responsible_vocabulary',
        ),
        required=True,
    )

    # reorder new added fields
    form.order_before(result_indicator='comments')
    form.order_before(priority='comments')
    form.order_before(planned_end_date='comments')
    form.order_before(representative_responsible='comments')
    form.order_before(administrative_responsible='comments')
    form.order_before(manager='comments')
    form.order_before(visible_for='comments')
    form.order_before(extra_concerned_people='comments')
    form.order_before(budget='comments')

    # hide some fields
    form.omitted('categories')
    form.omitted('planned_begin_date')
    form.omitted('effective_begin_date')
    form.omitted('effective_end_date')
    form.omitted('progress')


class OperationalObjective(Project):
    """ """
    implements(IOperationalObjective)


class RepresentativeResponsibleVocabulary(object):
    """
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        return getVocabularyTermsForOrganization(context, 'echevins')


class AdministrativeResponsibleVocabulary(object):
    """
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        return getVocabularyTermsForOrganization(context, 'services')


class OperationalObjectiveSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IOperationalObjective, )
