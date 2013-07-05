# -*- coding: utf-8 -*-

from zope.interface import implements

from plone.autoform import directives as form
from plone.dexterity.schema import DexteritySchemaPolicy

from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project


class IStrategicObjective(IProject):
    """
        StrategicObjective schema, field ordering
    """
    # omit some fields
    form.omitted('priority')
    form.omitted('budget')
    form.omitted('manager')
    form.omitted('visible_for')
    form.omitted('extra_concerned_people')
    form.omitted('result_indicator')
    form.omitted('planned_begin_date')
    form.omitted('effective_begin_date')
    form.omitted('planned_end_date')
    form.omitted('effective_end_date')
    form.omitted('progress')


class StrategicObjective(Project):
    """ """
    implements(IStrategicObjective)


class StrategicObjectiveSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IStrategicObjective, )
