# -*- coding: utf-8 -*-

from imio.project.pst import _
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationChoice
from zope.interface import implements
from collective.symlink.content.symlink import ISymlink, Symlink


class ISubActionLink(ISymlink):
    symbolic_link = RelationChoice(
        title=_(u"Symbolic link"),
        source=ObjPathSourceBinder(
            navigation_tree_query={"portal_type": ("pstsubaction",)},
            portal_type=("pstsubaction",),
            symlink_status=("void", "source")
        ),
        required=True,
    )


class SubActionLink(Symlink):
    implements(ISubActionLink)

    def Title(self):
        return super(SubActionLink, self).Title().replace('(SA', '(SAL')

