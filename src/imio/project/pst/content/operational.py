# -*- coding: utf-8 -*-

from dexterity.localrolesfield.field import LocalRolesField
from imio.project.core import _ as _c
from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project
from imio.project.core.utils import getProjectSpace
from imio.project.core.utils import getVocabularyTermsForOrganization
from imio.project.pst import _
from plone import api
from plone.autoform import directives as form
from plone.dexterity.schema import DexteritySchemaPolicy
from plone.dexterity.browser.view import DefaultView
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
        description=_(u"Choose principals that will be representative responsible for this project."),
        value_type=schema.Choice(
            vocabulary=u'imio.project.pst.content.operational.representative_responsible_vocabulary',
        ),
        required=True,
        min_length=1,
    )

    administrative_responsible = LocalRolesField(
        title=_(u"Administrative responsible"),
        description=_(u"Choose principals that will be administrative responsible for this project."),
        value_type=schema.Choice(
            vocabulary=u'imio.project.core.content.project.manager_vocabulary',
        ),
        required=True,
        min_length=1,
    )

    manager = LocalRolesField(
        title=_c(u"Manager"),
        description=_c(u"Choose principals that will manage this project."),
        value_type=schema.Choice(
            vocabulary='imio.project.core.content.project.manager_vocabulary'
        ),
        required=True,
        min_length=1,
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
    form.order_before(budget_comments='comments')
    form.order_before(observation='comments')

    # hide some fields
    form.omitted('visible_for')
    form.omitted('planned_begin_date')
    form.omitted('effective_begin_date')
    form.omitted('effective_end_date')
    form.omitted('progress')


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
        if self.field.__name__ == "planned_end_date":
            if self.context.planned_end_date:
                return self.context.planned_end_date

            try:
                uid = self.context.UID()
            except:
                uid = None
            if uid is None:
                return
            path = api.content.find(UID=self.context.UID())[0].getPath()
            act_planned_end_date = [
                act.planned_end_date
                for act in api.content.find(
                    path=path,
                    portal_type=["pstaction", "action_link", "pstsubaction"],
                )
            ]
            if act_planned_end_date:
                return max(act_planned_end_date)

        return super(OperationalObjectiveDataManager, self).get()


class RepresentativeResponsibleVocabulary(object):
    """
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """"""
        return getVocabularyTermsForOrganization(context, 'echevins', 'active')


class OperationalObjectiveSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IOperationalObjective, )


class ManagerVocabulary(object):
    """ Temporary class needed to access the site before migration. Can be removed after 1.0 """
    implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary([])


class OOView(DefaultView):
    """
        View form redefinition to customize fields.
    """

    def updateWidgets(self, prefix=None):
        super(OOView, self).updateWidgets()
        # import ipdb; ipdb.set_trace()
        pass  # Not used, only for tests
