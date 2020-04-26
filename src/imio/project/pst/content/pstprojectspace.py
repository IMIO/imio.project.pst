from plone.autoform import directives
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


class IPSTProjectSpace(IProjectSpace):
    """
        PST Project schema
    """
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

    directives.omitted('project_fields')

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
        return (IPSTProjectSpace, )


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
