# -*- coding: utf-8 -*-

from imio.project.pst import _
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationChoice
from zope.interface import implements
from collective.symlink.content.symlink import ISymlink, Symlink


class IActionLink(ISymlink):
    symbolic_link = RelationChoice(
        title=_(u"Symbolic link"),
        source=ObjPathSourceBinder(
            navigation_tree_query={"portal_type": ("pstaction",)},
            portal_type=("pstaction",),
            symlink_status=("void", "source")
        ),
        required=True,
    )


class ActionLink(Symlink):
    implements(IActionLink)

    def Title(self):
        return super(ActionLink, self).Title().replace('(A', '(AL')

