# -*- coding: utf-8 -*-

from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project
from imio.project.core.utils import getProjectSpace
from plone.autoform import directives as form
from plone.dexterity.schema import DexteritySchemaPolicy
from zope.interface import implements


class IStrategicObjective(IProject):
    """
        StrategicObjective schema, field ordering
    """
    # omit some fields
    form.omitted('priority')
    #form.omitted('budget')
    #form.omitted('budget_comments')
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

    def Title(self):
        if getattr(getProjectSpace(self), 'use_ref_number', True):
            return '%s (OS.%s)' % (self.title.encode('utf8'), self.reference_number)
        else:
            return self.title.encode('utf8')


class StrategicObjectiveSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IStrategicObjective, )
