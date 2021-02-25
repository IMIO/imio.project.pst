from plone.autoform import directives
from collective.eeafaceted.z3ctable import _ as _z
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from imio.project.core.content.projectspace import get_pt_fields_voc
from imio.project.core.content.projectspace import mandatory_check
from imio.project.core.content.projectspace import position_check
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.core.content.projectspace import ProjectSpace
from imio.project.core.content.projectspace import ProjectSpaceSchemaPolicy
from imio.project.core import _ as _c
from imio.project.pst import _
from zope import schema
from zope.interface import Interface
from zope.interface import implements
from zope.interface import invariant
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

STRATEGICOBJECTIVE_EXCLUDED_FIELDS = [
    'IDublinCore.description', 'IDublinCore.contributors', 'IDublinCore.creators', 'IDublinCore.effective',
    'IDublinCore.expires', 'IDublinCore.language', 'IDublinCore.rights', 'IDublinCore.subjects', 'INameFromTitle.title',
    'IVersionable.changeNote', 'effective_begin_date', 'effective_end_date', 'extra_concerned_people', 'manager',
    'notes', 'planned_begin_date', 'planned_end_date', 'priority', 'progress', 'result_indicator', 'visible_for'
]

OPERATIONALOBJECTIVE_EXCLUDED_FIELDS = [
    'IDublinCore.description', 'IDublinCore.contributors', 'IDublinCore.creators', 'IDublinCore.effective',
    'IDublinCore.expires', 'IDublinCore.language', 'IDublinCore.rights', 'IDublinCore.subjects', 'INameFromTitle.title',
    'IVersionable.changeNote', 'effective_begin_date', 'effective_end_date', 'notes', 'planned_begin_date', 'progress',
    'visible_for'
]

PSTACTION_EXCLUDED_FIELDS = [
    'IDublinCore.description', 'IDublinCore.contributors', 'IDublinCore.creators', 'IDublinCore.effective',
    'IDublinCore.expires', 'IDublinCore.language', 'IDublinCore.rights', 'IDublinCore.subjects', 'INameFromTitle.title',
    'IVersionable.changeNote', 'budget_split', 'notes', 'priority', 'visible_for'
]

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

StrategicObjectivesColumnsVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'select_row', title=_z(u'select_row')),
     SimpleTerm(value=u'pretty_link', title=_z(u'pretty_link')),
     SimpleTerm(value=u'review_state', title=_z(u'header_review_state')),
     SimpleTerm(value=u'categories', title=_c(u'Categories')),
     SimpleTerm(value=u'CreationDate', title=_z(u'header_CreationDate')),
     SimpleTerm(value=u'ModificationDate', title=_z(u'header_ModificationDate')),
     SimpleTerm(value=u'history_actions', title=_z(u'history_actions'))]
)

OperationalObjectivesColumnsVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'select_row', title=_z(u'select_row')),
     SimpleTerm(value=u'pretty_link', title=_z(u'pretty_link')),
     SimpleTerm(value=u'parents', title=_z(u'header_parents')),
     SimpleTerm(value=u'review_state', title=_z(u'header_review_state')),
     SimpleTerm(value=u'manager', title=_z(u'header_manager')),
     SimpleTerm(value=u'planned_end_date', title=_z(u'header_planned_end_date')),
     SimpleTerm(value=u'priority', title=_z(u'header_priority')),
     SimpleTerm(value=u'categories', title=_c(u'Categories')),
     SimpleTerm(value=u'sdgs', title=_z(u'header_sdgs')),
     SimpleTerm(value=u'CreationDate', title=_z(u'header_CreationDate')),
     SimpleTerm(value=u'ModificationDate', title=_z(u'header_ModificationDate')),
     SimpleTerm(value=u'history_actions', title=_z(u'history_actions'))]
)

PstactionColumnsVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'select_row', title=_z(u'select_row')),
     SimpleTerm(value=u'pretty_link', title=_z(u'pretty_link')),
     SimpleTerm(value=u'parents', title=_z(u'header_parents')),
     SimpleTerm(value=u'review_state', title=_z(u'header_review_state')),
     SimpleTerm(value=u'manager', title=_z(u'header_manager')),
     SimpleTerm(value=u'responsible', title=_z(u'header_responsible')),
     SimpleTerm(value=u'planned_begin_date', title=_z(u'header_planned_begin_date')),
     SimpleTerm(value=u'planned_end_date', title=_z(u'header_planned_end_date')),
     SimpleTerm(value=u'effective_begin_date', title=_z(u'header_effective_begin_date')),
     SimpleTerm(value=u'effective_end_date', title=_z(u'header_effective_end_date')),
     SimpleTerm(value=u'progress', title=_z(u'header_progress')),
     SimpleTerm(value=u'health_indicator', title=_z(u'header_health_indicator')),
     SimpleTerm(value=u'categories', title=_c(u'Categories')),
     SimpleTerm(value=u'sdgs', title=_z(u'header_sdgs')),
     SimpleTerm(value=u'CreationDate', title=_z(u'header_CreationDate')),
     SimpleTerm(value=u'ModificationDate', title=_z(u'header_ModificationDate')),
     SimpleTerm(value=u'history_actions', title=_z(u'history_actions'))]
)

TasksColumnsVocabulary = SimpleVocabulary(
    [SimpleTerm(value=u'select_row', title=_z(u'select_row')),
     SimpleTerm(value=u'pretty_link', title=_z(u'pretty_link')),
     SimpleTerm(value=u'parents', title=_z(u'header_parents')),
     SimpleTerm(value=u'review_state', title=_z(u'header_review_state')),
     SimpleTerm(value=u'assigned_group', title=_z(u'header_assigned_group')),
     SimpleTerm(value=u'assigned_user', title=_z(u'header_assigned_user')),
     SimpleTerm(value=u'due_date', title=_z(u'header_due_date')),
     SimpleTerm(value=u'CreationDate', title=_z(u'header_CreationDate')),
     SimpleTerm(value=u'ModificationDate', title=_z(u'header_ModificationDate')),
     SimpleTerm(value=u'history_actions', title=_z(u'history_actions'))]
)


class IStrategicObjectiveFieldsSchema(Interface):
    field_name = schema.Choice(
        title=_(u'Field name'),
        vocabulary=u'imio.project.pst.SOFieldsVocabulary',
    )

    read_tal_condition = schema.TextLine(
        title=_("Read TAL condition"),
        required=False,
    )

    write_tal_condition = schema.TextLine(
        title=_("Write TAL condition"),
        required=False,
    )


class IOperationalObjectiveFieldsSchema(Interface):
    field_name = schema.Choice(
        title=_(u'Field name'),
        vocabulary=u'imio.project.pst.OOFieldsVocabulary',
    )

    read_tal_condition = schema.TextLine(
        title=_("Read TAL condition"),
        required=False,
    )

    write_tal_condition = schema.TextLine(
        title=_("Write TAL condition"),
        required=False,
    )


class IPSTActionFieldsSchema(Interface):
    field_name = schema.Choice(
        title=_(u'Field name'),
        vocabulary=u'imio.project.pst.ActionFieldsVocabulary',
    )

    read_tal_condition = schema.TextLine(
        title=_("Read TAL condition"),
        required=False,
    )

    write_tal_condition = schema.TextLine(
        title=_("Write TAL condition"),
        required=False,
    )


class IPSTProjectSpace(IProjectSpace):
    """
        PST Project schema
    """
    strategicobjective_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('StrategicObjective')}),
        description=_(u'Warning ! Completion of these fields requires a good knowledge of the TAL language. '
                      u'Be sure to get help from the product support team.'),
        required=False,
        value_type=DictRow(title=_(u'Field'),
                           schema=IStrategicObjectiveFieldsSchema,
                           required=False),
    )
    directives.widget('strategicobjective_fields', DataGridFieldFactory, display_table_css_class='listing',
                      allow_reorder=True, auto_append=False)

    operationalobjective_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('OperationalObjective')}),
        description=_(u'Warning ! Completion of these fields requires a good knowledge of the TAL language. '
                      u'Be sure to get help from the product support team.'),
        required=False,
        value_type=DictRow(title=_(u'Field'),
                           schema=IOperationalObjectiveFieldsSchema,
                           required=False),
    )
    directives.widget('operationalobjective_fields', DataGridFieldFactory, display_table_css_class='listing',
                      allow_reorder=True, auto_append=False)

    pstaction_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('PSTAction')}),
        description=_(u'Warning ! Completion of these fields requires a good knowledge of the TAL language. '
                      u'Be sure to get help from the product support team.'),
        required=False,
        value_type=DictRow(title=_(u'Field'),
                           schema=IPSTActionFieldsSchema,
                           required=False),
    )
    directives.widget('pstaction_fields', DataGridFieldFactory, display_table_css_class='listing',
                      allow_reorder=True, auto_append=False)

    # this field will be hidden
    pstsubaction_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('PSTSubAction')}),
        required=False,
        value_type=DictRow(title=_(u'Field'),
                           schema=IPSTActionFieldsSchema,
                           required=False),
    )
    directives.widget('pstsubaction_fields', DataGridFieldFactory, display_table_css_class='listing',
                      allow_reorder=True, auto_append=False)

    strategicobjectives_columns = schema.List(
        title=_(u"StrategicObjective columns"),
        # description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=StrategicObjectivesColumnsVocabulary),
    )

    operationalobjectives_columns = schema.List(
        title=_(u"OperationalObjective columns"),
        # description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=OperationalObjectivesColumnsVocabulary),
    )

    pstactions_columns = schema.List(
        title=_(u"PSTAction columns"),
        #  description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=PstactionColumnsVocabulary),
    )

    tasks_columns = schema.List(
        title=_(u"Tasks columns"),
        # description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=TasksColumnsVocabulary),
    )

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

    directives.omitted('project_fields')
    directives.omitted('project_budget_states')
    # when pstaction_fields modified pstsubaction_fields is updated with his values
    directives.omitted('pstsubaction_fields')
    directives.omitted('pstsubaction_budget_states')

    @invariant
    def validateSettings(data):
        mandatory_check(data, field_constraints)
        position_check(data, field_constraints)


class PSTProjectSpace(ProjectSpace):
    """ """
    implements(IPSTProjectSpace)


class PSTProjectSpaceSchemaPolicy(ProjectSpaceSchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IPSTProjectSpace,)


class SOFieldsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return get_pt_fields_voc('strategicobjective', STRATEGICOBJECTIVE_EXCLUDED_FIELDS, field_constraints)


class OOFieldsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return get_pt_fields_voc('operationalobjective', OPERATIONALOBJECTIVE_EXCLUDED_FIELDS, field_constraints)


class ActionFieldsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        return get_pt_fields_voc('pstaction', PSTACTION_EXCLUDED_FIELDS, field_constraints)
