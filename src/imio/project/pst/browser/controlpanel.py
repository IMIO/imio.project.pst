# -*- coding: utf-8 -*-

from imio.project.core import _ as _c
from imio.project.core.browser.controlpanel import get_pt_fields_voc
from imio.project.core.browser.controlpanel import mandatory_check
from imio.project.core.browser.controlpanel import position_check
from imio.project.pst import _
from plone import api
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.utils import remove
from z3c.form import form
from zope import schema
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implements
from zope.interface import Interface
from zope.interface import invariant
from zope.interface import Invalid
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


field_constraints = {
    'titles': {},
    'mandatory': {'strategicobjective': ['IDublinCore.title'],
                  'operationalobjective': ['IDublinCore.title'],
                  'pstaction': ['IDublinCore.title'],
                  },
    'indexes': {'strategicobjective': [('IDublinCore.title', 1)],
                'operationalobjective': [('IDublinCore.title', 1)],
                'pstaction': [('IDublinCore.title', 1)],
                },
    'empty': {'strategicobjective': [],
              'operationalobjective': [],
              'pstaction': [],
              },
}


class SOFieldsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return get_pt_fields_voc('strategicobjective',
                                 ['IDublinCore.description', 'IDublinCore.contributors', 'IDublinCore.creators',
                                  'IDublinCore.effective', 'IDublinCore.expires', 'IDublinCore.language',
                                  'IDublinCore.rights', 'IDublinCore.subjects', 'INameFromTitle.title',
                                  'IVersionable.changeNote', 'effective_begin_date', 'effective_end_date',
                                  'extra_concerned_people', 'manager', 'notes', 'planned_begin_date',
                                  'planned_end_date', 'priority', 'progress', 'result_indicator', 'visible_for'],
                                 field_constraints)


class OOFieldsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return get_pt_fields_voc('operationalobjective',
                                 ['IDublinCore.description', 'IDublinCore.contributors', 'IDublinCore.creators',
                                  'IDublinCore.effective', 'IDublinCore.expires', 'IDublinCore.language',
                                  'IDublinCore.rights', 'IDublinCore.subjects', 'INameFromTitle.title',
                                  'IVersionable.changeNote', 'effective_begin_date', 'effective_end_date', 'notes',
                                  'planned_begin_date', 'progress', 'visible_for'],
                                 field_constraints)


class ActionFieldsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return get_pt_fields_voc('pstaction',
                                 ['IDublinCore.description', 'IDublinCore.contributors', 'IDublinCore.creators',
                                  'IDublinCore.effective', 'IDublinCore.expires', 'IDublinCore.language',
                                  'IDublinCore.rights', 'IDublinCore.subjects', 'INameFromTitle.title',
                                  'IVersionable.changeNote', 'notes', 'priority', 'visible_for'],
                                 field_constraints)


class SubActionFieldsVocabulary(object):
    """ Not used """
    implements(IVocabularyFactory)

    def __call__(self, context):
        return get_pt_fields_voc('pstsubaction',
                                 ['IDublinCore.description', 'IDublinCore.contributors', 'IDublinCore.creators',
                                  'IDublinCore.effective', 'IDublinCore.expires', 'IDublinCore.language',
                                  'IDublinCore.rights', 'IDublinCore.subjects', 'INameFromTitle.title',
                                  'IVersionable.changeNote', 'notes', 'priority', 'visible_for'],
                                 field_constraints)


class BudgetGlobalizationStatesVocabulary(object):
    """ Workflow states of PST content types """
    implements(IVocabularyFactory)

    def __call__(self, context):
        """Finds workflows relevant to PST, then finds their possible states"""

        portal_workflow = api.portal.get_tool('portal_workflow')

        workflow_ids = set([])
        for portal_type in ('strategicobjective', 'operationalobjective', 'pstaction', 'pstsubaction'):
            wf_ids = portal_workflow.getChainFor(portal_type)
            if wf_ids:
                workflow_ids.add(wf_ids[0])

        states = set([])
        for workflow_id in workflow_ids:
            workflow = portal_workflow.getWorkflowById(workflow_id)
            for workflow_state in workflow.states.values():
                states.add((workflow_state.id, workflow_state.title))

        request = getRequest()
        terms = [SimpleTerm(state_id, title=translate(state_title, domain='plone', context=request)) for
                 state_id, state_title in states]
        return SimpleVocabulary(terms)


class IImioPSTSettings(Interface):
    """"""

    strategicobjective_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('StrategicObjective')}),
        description=_c(u"Put fields on the right to display it. Flags are : ..."),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.SOFieldsVocabulary'),
#        value_type=schema.Choice(source=IMFields),  # a source is not managed by registry !!
    )

    operationalobjective_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('OperationalObjective')}),
#        description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.OOFieldsVocabulary'),
    )

    pstaction_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('PSTAction')}),
#        description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.ActionFieldsVocabulary'),
    )

    # this field will be hidden
    pstsubaction_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('PSTSubAction')}),
#        description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.ActionFieldsVocabulary'),
    )

    budget_globalization_states = schema.List(
        title=_(u"Budget globalization states"),
        description=_(u"PST content in these states will be taken into account for budget globalization"),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.BudgetGlobalizationStatesVocabulary'),
    )

    @invariant
    def validateSettings(data):
        mandatory_check(data, field_constraints)
        position_check(data, field_constraints)


class SettingsEditForm(RegistryEditForm):
    """"""

    form.extends(RegistryEditForm)
    schema = IImioPSTSettings
    schema_prefix = 'imio.project.settings'
    label = _(u"PST settings")

    def updateFields(self):
        super(SettingsEditForm, self).updateFields()
        remove(self, 'pstsubaction_fields')


SettingsView = layout.wrap_form(SettingsEditForm, ControlPanelFormWrapper)
