from zope.interface import implements

from plone.dexterity.schema import DexteritySchemaPolicy

from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project


class IStrategicObjective(IProject):
    """
        StrategicObjective schema, field ordering
    """


class StrategicObjective(Project):
    """ """
    implements(IStrategicObjective)


class ProjectSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IStrategicObjective, )
