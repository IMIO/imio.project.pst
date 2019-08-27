# -*- coding: utf-8 -*-
"""Custom viewlets."""

from Acquisition import aq_parent, aq_inner
from collective.task.browser.viewlets import TasksListViewlet as OriginalTasksListViewlet
from collective.messagesviewlet.message import generate_uid
from collective.messagesviewlet.browser.messagesviewlet import MessagesViewlet
from collective.messagesviewlet.message import PseudoMessage
from imio.helpers.content import richtextval
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.layout.viewlets import ViewletBase
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zc.relation.interfaces import ICatalog
from zope.i18n import translate
from zope.security import checkPermission


class TasksListViewlet(OriginalTasksListViewlet):

    """Tasks list for current task container object."""

    def update(self):
        if self.context.portal_type in ('task', ):
            super(TasksListViewlet, self).update()

    def render(self):
        if self.context.portal_type in ('task', ):
            return super(TasksListViewlet, self).render()
        else:
            return ""


class ContentLinkViewlet(ViewletBase):

    index = ViewPageTemplateFile("contentlink.pt")

    def content_link(self):
        if self.back_references(self.context):
            return [obj.aq_parent for obj in self.context.back_references()]
        if hasattr(self.context, "_link_portal_type"):
            ref = [
                obj for obj in self.context.symbolic_link.to_object.back_references()
            ]
            ref.append(self.context.symbolic_link.to_object)
            return [
                obj.aq_parent
                for obj in ref
                if obj.absolute_url() != self.context.absolute_url()
            ]

    def back_references(self, context):
        """
        Return back references from source object on specified attribute_name
        """
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = []
        for rel in catalog.findRelations(
            dict(to_id=intids.getId(aq_inner(context)), from_attribute="symbolic_link")
        ):
            obj = intids.queryObject(rel.from_id)
            if obj is not None and checkPermission("zope2.View", obj):
                result.append(obj)
        return result


class ContextInformationViewlet(MessagesViewlet):
    """
        Viewlet displaying context information
    """

    def getAllMessages(self):
        ret = []
        if hasattr(self.context, "_link_portal_type"):

            msg = translate(
                u"This content is a copy, to modify the original content click on this button ${edit}",
                domain="imio.project.pst",
                context=self.request,
                mapping={
                    "edit": '<a href="{0}/edit">Edit</a>'.format(
                        self.context.symbolic_link.to_object.absolute_url()
                    )
                },
            )
            ret.append(
                PseudoMessage(
                    msg_type="significant",
                    text=richtextval(msg),
                    hidden_uid=generate_uid(),
                    can_hide=False,
                )
            )

        if self.context.portal_type == "operationalobjective":
            if self.context.planned_end_date:
                act_planned_end_date = [
                    act.planned_end_date
                    for act in api.content.find(
                        context=self.context,
                        portal_type=["pstaction", "action_link", "pstsubaction"],
                    )
                ]
                if act_planned_end_date:
                    if max(act_planned_end_date) > self.context.planned_end_date:
                        msg = translate(
                            u"The planned end date of any one of the actions is greater than the planned end date of the operational objective",
                            domain="imio.project.pst",
                            context=self.request,
                        )
                        ret.append(
                            PseudoMessage(
                                msg_type="significant",
                                text=richtextval(msg),
                                hidden_uid=generate_uid(),
                                can_hide=False,
                            )
                        )

        return ret
