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


class SettingsEditForm(RegistryEditForm):
    """"""

    form.extends(RegistryEditForm)
    schema = IImioPSTSettings
    schema_prefix = 'imio.project.settings'
    label = _(u"PST settings")


SettingsView = layout.wrap_form(SettingsEditForm, ControlPanelFormWrapper)
