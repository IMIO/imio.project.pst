# -*- coding: utf-8 -*-

from dexterity.localrolesfield.field import LocalRolesField
from imio.project.core import _ as _c
from imio.project.core.browser.views import ProjectAddForm
from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project
from imio.project.core.utils import getProjectSpace
from imio.project.core.utils import getVocabularyTermsForOrganization
from imio.project.pst import _
from imio.project.pst.utils import find_max_deadline_on_children
from plone import api
from plone.autoform import directives as form
from plone.dexterity.schema import DexteritySchemaPolicy
from plone.dexterity.browser.add import DefaultAddView
from z3c.form.datamanager import AttributeField
from z3c.form.interfaces import IDataManager
from zope import schema
from zope.interface import implements
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class IOperationalObjective(IProject):
    """
        OperationalObjective schema, field ordering
    """
    representative_responsible = LocalRolesField(
        title=_(u"Representative responsible"),
        # description=_(u"Choose principals that will be representative responsible for this project."),
        value_type=schema.Choice(
            vocabulary=u'imio.project.pst.content.operational.representative_responsible_vocabulary',
        ),
        required=True,
        min_length=1,
    )

    administrative_responsible = LocalRolesField(
        title=_(u"Administrative responsible"),
        # description=_(u"Choose principals that will be administrative responsible for this project."),
        value_type=schema.Choice(
            vocabulary=u'imio.project.core.content.project.manager_vocabulary',
        ),
        required=True,
        min_length=1,
    )

    manager = LocalRolesField(
        title=_c(u"Manager"),
        # description=_c(u"Choose principals that will manage this project."),
        value_type=schema.Choice(
            vocabulary='imio.project.core.content.project.manager_vocabulary'
        ),
        required=True,
        min_length=1,
    )


class OperationalObjective(Project):
    """ """
    implements(IOperationalObjective)

    def Title(self):
        if getattr(getProjectSpace(self), 'use_ref_number', True):
            return '%s (OO.%s)' % (self.title.encode('utf8'), self.reference_number)
        else:
            return self.title.encode("utf8")


@implementer(IDataManager)
class OperationalObjectiveDataManager(AttributeField):
    def get(self):
        value = super(OperationalObjectiveDataManager, self).get()
        if self.field.__name__ == "planned_end_date":
            value = self.context.planned_end_date
            if not value:
                value = find_max_deadline_on_children(
                    self.context,
                    {
                        "pstaction": "planned_end_date",
                        "pstsubaction": "planned_end_date",
                        "subaction_link": "planned_end_date",
                        "task": "due_date"
                    }
                )
        return value


class RepresentativeResponsibleVocabulary(object):
    """
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        return getVocabularyTermsForOrganization(context, 'echevins', 'active', sort_on='getObjPositionInParent')


class OperationalObjectiveSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IOperationalObjective,)


class ManagerVocabulary(object):
    """
        Temporary class needed to access the site before migration.
        Can be removed after 1.3 migration
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([])


class OOAddForm(ProjectAddForm):
    portal_type = 'operationalobjective'


class OOAdd(DefaultAddView):
    form = OOAddForm
