# -*- coding: utf-8 -*-

from imio.project.core import _ as _c
from imio.project.pst import _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.utils import remove
from z3c.form import form
from zope import schema
from zope.interface import Interface


class IImioPSTSettings(Interface):
    """"""
    strategicobjective_budget_states = schema.List(
        title=_c(u"${type} budget globalization states", mapping={'type': _('StrategicObjective')}),
        description=_c(u'Put states on the right for which you want to globalize budget fields.'),
        required=False,
        value_type=schema.Choice(vocabulary=u'imio.project.pst.SOReviewStatesVocabulary'),
    )

    operationalobjective_budget_states = schema.List(
        title=_c(u"${type} budget globalization states", mapping={'type': _('OperationalObjective')}),
        # description=_c(u'Put states on the right for which you want to globalize budget fields.'),
        required=False,
        value_type=schema.Choice(vocabulary=u'imio.project.pst.OOReviewStatesVocabulary'),
    )

    pstaction_budget_states = schema.List(
        title=_c(u"${type} budget globalization states", mapping={'type': _('PSTAction')}),
        # description=_c(u'Put states on the right for which you want to globalize budget fields.'),
        required=False,
        value_type=schema.Choice(vocabulary=u'imio.project.pst.PSTActionReviewStatesVocabulary'),
    )

    # this field will be hidden
    pstsubaction_budget_states = schema.List(
        title=_c(u"${type} budget globalization states", mapping={'type': _('PSTSubAction')}),
        # description=_c(u'Put states on the right for which you want to globalize budget fields.'),
        required=False,
        value_type=schema.Choice(vocabulary=u'imio.project.pst.PSTActionReviewStatesVocabulary'),
    )


class SettingsEditForm(RegistryEditForm):
    """"""

    form.extends(RegistryEditForm)
    schema = IImioPSTSettings
    schema_prefix = 'imio.project.settings'
    label = _(u"PST settings")

    def updateFields(self):
        super(SettingsEditForm, self).updateFields()
        remove(self, 'pstsubaction_fields')
        remove(self, 'pstsubaction_budget_states')


SettingsView = layout.wrap_form(SettingsEditForm, ControlPanelFormWrapper)
