# -*- coding: utf-8 -*-
from plone.dexterity.content import Container

from collective.contact.plonegroup.utils import organizations_with_suffixes
from collective.task.interfaces import ITaskContent
from dexterity.localrolesfield.field import LocalRolesField
from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project
from imio.project.core.utils import getProjectSpace
from imio.project.pst import _
from plone import api
from plone.autoform import directives as form
from plone.dexterity.schema import DexteritySchemaPolicy
from plone.directives.form import default_value
from z3c.form import validator
from zope import schema
from zope.interface import implements
from zope.interface import Invalid
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog


class IPSTAction(IProject):
    """
        PSTAction schema, field ordering
    """

    representative_responsible = LocalRolesField(
        title=_(u"Representative responsible"),
        description=_(u"Choose principals that will be representative responsible for this project. "
                      u"If nothing choosed, the oo value is used for searches."),
        value_type=schema.Choice(
            vocabulary=u'imio.project.pst.content.operational.representative_responsible_vocabulary',
        ),
        required=False,
    )

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

    # reorder fields
    form.order_before(planned_end_date='comments')
    form.order_before(planned_begin_date='comments')
    form.order_before(effective_begin_date='comments')
    form.order_before(effective_end_date='comments')
    form.order_before(progress='comments')
    form.order_before(health_indicator='comments')
    form.order_before(health_indicator_details='comments')
    form.order_before(representative_responsible='comments')
    form.order_before(manager='comments')
    form.order_before(visible_for='comments')
    form.order_before(extra_concerned_people='comments')
    form.order_before(budget='comments')
    form.order_before(budget_comments='comments')
    form.order_before(observation='comments')

    # hide some fields
    form.omitted('visible_for')
    form.omitted('priority')


# We add a default value for the pstaction. This works but changes on other field params don't work.
#IPSTAction['manager'].defaultFactory = default_manager

@default_value(field=IPSTAction['manager'])
def default_manager(data):
    if not data.context.portal_type == 'operationalobjective':
        return []
    member_groups = api.group.get_groups(user=api.user.get_current())
    orgs = organizations_with_suffixes(member_groups, ['actioneditor'])
    return [org for org in data.context.manager if org in orgs]


class ManagerFieldValidator(validator.SimpleFieldValidator):
    def validate(self, value):
        #we call the already defined validators
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

#validator.WidgetValidatorDiscriminators(ManagerFieldValidator, field=IPSTAction['manager'])
#provideAdapter(ManagerFieldValidator)


class PSTAction(Project):
    """ """
    implements(IPSTAction)
    # we block local roles acquisition
    __ac_local_roles_block__ = True

    def Title(self):
        if getattr(getProjectSpace(self), 'use_ref_number', True):
            return '%s (A.%s)' % (self.title.encode('utf8'), self.reference_number)
        else:
            return self.title.encode('utf8')

    def back_references(self):
        """
        Return back references from source object on specified attribute_name
        """
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = []
        for rel in catalog.findRelations(
                dict(to_id=intids.getId(aq_inner(self)),
                     from_attribute='symbolic_link')
        ):
            obj = intids.queryObject(rel.from_id)
            if obj is not None and checkPermission('zope2.View', obj):
                result.append(obj)
        return result

    def allowedContentTypes(self):
        allowed = super(Container, self).allowedContentTypes()
        for item in self.listFolderContents():
            if IPSTSubAction.providedBy(item):
                allowed = [fti for fti in allowed if fti.id != 'task']
                break
            if ITaskContent.providedBy(item):
                allowed = [fti for fti in allowed if fti.id != 'subaction_link']
                break
        return allowed


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
            return self.title.encode('utf8')
