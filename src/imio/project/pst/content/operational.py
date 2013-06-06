from zope.interface import implements

from plone.dexterity.schema import DexteritySchemaPolicy

from imio.project.core.content.project import IProject
from imio.project.core.content.project import Project


class IOperationalObjective(IProject):
    """
        OperationalObjective schema, field ordering
    """


class OperationalObjective(Project):
    """ """
    implements(IOperationalObjective)


class OperationalObjectiveSchemaPolicy(DexteritySchemaPolicy):
    """ """

    def bases(self, schemaName, tree):
        return (IOperationalObjective, )
