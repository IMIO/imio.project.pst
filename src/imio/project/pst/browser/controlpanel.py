# -*- coding: utf-8 -*-

from imio.project.core import _ as _c
from imio.project.core.browser.controlpanel import get_pt_fields_voc
from imio.project.core.browser.controlpanel import mandatory_check
from imio.project.pst import _
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from z3c.form import form
from zope import schema
from zope.interface import implements
from zope.interface import Interface
from zope.interface import invariant
from zope.interface import Invalid
from zope.schema.interfaces import IVocabularyFactory


mandatory_fields = {'strategicobjective': ['IDublinCore.title', 'IDublinCore.description'],
#                    'operationalobjective': ['IDublinCore.title', 'IDublinCore.description'],
#                    'pstaction': [],
#                    'pstsubaction': [],
                    }


class SOFieldsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return get_pt_fields_voc('strategicobjective',
                                 ['IDublinCore.contributors', 'IDublinCore.creators', 'IDublinCore.effective',
                                  'IDublinCore.expires', 'IDublinCore.language', 'IDublinCore.rights',
                                  'IDublinCore.subjects', 'INameFromTitle.title', 'IVersionable.changeNote',
                                  'effective_begin_date', 'effective_end_date', 'extra_concerned_people', 'manager',
                                  'notes', 'planned_begin_date', 'planned_end_date', 'priority', 'progress',
                                  'result_indicator', 'visible_for'],
                                 mandatory_fields)


class IImioPSTSettings(Interface):
    """"""

    strategicobjective_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('StrategicObjective')}),
        description=_c(u'Put fields on the right to display it. Fields with asterisk are mandatory !'),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.SOFieldsVocabulary'),
#        value_type=schema.Choice(source=IMFields),  # a source is not managed by registry !!
    )

    @invariant
    def validateSettings(data):
        mandatory_check(data, mandatory_fields)


class SettingsEditForm(RegistryEditForm):
    """"""

    form.extends(RegistryEditForm)
    schema = IImioPSTSettings
    schema_prefix = 'imio.project.settings'
    label = _(u"PST settings")


SettingsView = layout.wrap_form(SettingsEditForm, ControlPanelFormWrapper)
