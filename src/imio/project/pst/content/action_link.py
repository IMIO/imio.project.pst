# -*- coding: utf-8 -*-

from collective.symlink.content.symlink import ISymlink, Symlink
from imio.project.pst import _
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationChoice
from zope.interface import implementer


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


@implementer(IActionLink)
class ActionLink(Symlink):
    """"""
