# -*- coding: utf-8 -*-

from imio.project.core.browser.views import ProjectAddForm
from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project
from imio.project.core.utils import getProjectSpace
from plone.dexterity.browser.add import DefaultAddView
from plone.dexterity.schema import DexteritySchemaPolicy
from zope.interface import implements


class IStrategicObjective(IProject):
    """
        StrategicObjective schema, field ordering
    """


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


class SOAddForm(ProjectAddForm):

    portal_type = 'strategicobjective'


class SOAdd(DefaultAddView):

    form = SOAddForm
