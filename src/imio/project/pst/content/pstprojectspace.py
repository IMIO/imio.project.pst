from plone.autoform import directives
from collective.eeafaceted.z3ctable import _ as _z
from imio.project.core.content.projectspace import get_pt_fields_voc
from imio.project.core.content.projectspace import mandatory_check
from imio.project.core.content.projectspace import position_check
from imio.project.core.content.projectspace import IProjectSpace
from imio.project.core.content.projectspace import ProjectSpace
from imio.project.core.content.projectspace import ProjectSpaceSchemaPolicy
from imio.project.core import _ as _c
from imio.project.pst import _
from zope import schema
from zope.interface import implements
from zope.interface import invariant
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


class IPSTProjectSpace(IProjectSpace):
    """
        PST Project schema
    """
    strategicobjective_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('StrategicObjective')}),
        description=_c(u"Put fields on the right to display it. Flags are : ..."),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.SOFieldsVocabulary'),
        # value_type=schema.Choice(source=IMFields),  # a source is not managed by registry !!
    )

    operationalobjective_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('OperationalObjective')}),
        # description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.OOFieldsVocabulary'),
    )

    pstaction_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('PSTAction')}),
        # description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.ActionFieldsVocabulary'),
    )

    pstsubaction_fields = schema.List(
        title=_c(u"${type} fields display", mapping={'type': _('PSTSubAction')}),
        # description=_c(u'Put fields on the right to display it. Flags are : ...'),
        value_type=schema.Choice(vocabulary=u'imio.project.pst.ActionFieldsVocabulary'),
    )

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

    directives.omitted('project_fields')
    # when pstaction_fields modified pstsubaction_fields is updated with his values
    directives.omitted('pstsubaction_fields')

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