# -*- coding: utf-8 -*-
"""Custom viewlets."""

from zc.relation.interfaces import ICatalog

from Acquisition import aq_inner
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.messagesviewlet.browser.messagesviewlet import MessagesViewlet
from collective.messagesviewlet.message import PseudoMessage
from collective.messagesviewlet.message import generate_uid
from collective.symlink.utils import is_linked_object
from collective.task.browser.viewlets import TasksListViewlet as OriginalTasksListViewlet
from imio.helpers.content import richtextval
from imio.prettylink.interfaces import IPrettyLink
from imio.project.core.content.project import IProject
from imio.project.core.utils import getProjectSpace
from imio.project.pst import _tr
from imio.project.pst.utils import find_max_deadline_on_children, is_smaller_deadline_on_parents
from plone.app.layout.viewlets import ViewletBase
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission

_ = _tr


class PrettyLinkTitleViewlet(ViewletBase):
    """
        Viewlet displaying a pretty link title
    """

    def adapted(self, showColors=False, display_tag_title=False, isViewable=True):
        plo = IPrettyLink(self.context)
        plo.showContentIcon = True
        plo.showColors = showColors
        plo.display_tag_title = display_tag_title
        plo.isViewable = isViewable
        plo.notViewableHelpMessage = ''
        return plo


class ActionPrettyLinkTitleViewlet(PrettyLinkTitleViewlet):
    """
        Viewlet displaying a pretty link title
    """

    def adapted(self, showColors=False, display_tag_title=False, isViewable=True):
        plo = super(ActionPrettyLinkTitleViewlet, self).adapted()
        if base_hasattr(plo.context, '_link_portal_type'):
            plo.showContentIcon = False
            plo.additionalCSSClasses = ['contenttype-{}'.format(plo.context._link_portal_type)]
        return plo


class TasksListViewlet(OriginalTasksListViewlet):
    """Tasks list for current task container object."""

    def update(self):
        if self.context.portal_type in ('task',):
            super(TasksListViewlet, self).update()

    def render(self):
        if self.context.portal_type in ('task',):
            return super(TasksListViewlet, self).render()
        else:
            return ""


class ContentLinkViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/contentlink.pt")

    def content_link(self):
        if self.back_references(self.context):
            return [obj.aq_parent for obj in self.back_references(self.context)]
        if hasattr(self.context, "_link_portal_type"):
            ref = [obj for obj in self.back_references(self.context.symbolic_link.to_object)]
            ref.append(self.context.symbolic_link.to_object)
            return [obj.aq_parent for obj in ref
                    if obj.absolute_url() != self.context.absolute_url()]

    def budget_split_url(self):
        if self.back_references(self.context) or hasattr(self.context, "_link_portal_type"):
            return '{}/@@budget_split'.format(self.context.absolute_url())

    def back_references(self, context):
        """
        Return back references from source object on specified attribute_name
        """
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = []
        for rel in catalog.findRelations(dict(to_id=intids.getId(aq_inner(context)), from_attribute="symbolic_link")):
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
        link_type, symlink_obj, original_obj, subpath = is_linked_object(self.context)
        if link_type:
            if subpath:
                linked_context = original_obj.restrictedTraverse(subpath)
            else:
                linked_context = original_obj
            msg = _(u"This content is a copy, to modify the original content click on this button ${edit}",
                    mapping={"edit": '<a href="{0}/edit">{1}</a>'.format(
                        linked_context.absolute_url(),
                        _tr('Edit', domain='plone'))})
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
                max_children_deadline = find_max_deadline_on_children(
                    self.context,
                    {
                        "pstaction": "planned_end_date",
                        "action_link": "planned_end_date",
                        "pstsubaction": "planned_end_date",
                        "subaction_link": "planned_end_date",
                        "task": "due_date"
                    }
                )
                if max_children_deadline:
                    if max_children_deadline > self.context.planned_end_date:
                        msg = _(u"The deadline of any one of children is greater than those of this element")
                        ret.append(
                            PseudoMessage(
                                msg_type="significant",
                                text=richtextval(msg),
                                hidden_uid=generate_uid(),
                                can_hide=False,
                            )
                        )
            else:
                msg = _(u"The deadline is not fill on this element, the system displays the largest of its "
                        u"possible children")
                ret.append(
                    PseudoMessage(
                        msg_type="significant",
                        text=richtextval(msg),
                        hidden_uid=generate_uid(),
                        can_hide=False,
                    )
                )
        if self.context.portal_type == "pstaction":
            if self.context.planned_end_date:
                max_children_deadline = find_max_deadline_on_children(
                    self.context,
                    {
                        "pstsubaction": "planned_end_date",
                        "subaction_link": "planned_end_date",
                        "task": "due_date"
                    }
                )
                if max_children_deadline:
                    if max_children_deadline > self.context.planned_end_date:
                        msg = _(u"The deadline of any one of children is greater than those of this element")
                        ret.append(
                            PseudoMessage(
                                msg_type="significant",
                                text=richtextval(msg),
                                hidden_uid=generate_uid(),
                                can_hide=False,
                            )
                        )
                if is_smaller_deadline_on_parents(self.context, {"pstaction": "planned_end_date",
                                                                 "operationalobjective": "planned_end_date"}):
                    msg = _(u"The deadline of this element is greater than one of its parents")
                    ret.append(
                        PseudoMessage(
                            msg_type="significant",
                            text=richtextval(msg),
                            hidden_uid=generate_uid(),
                            can_hide=False,
                        )
                    )
            else:
                msg = _(u"The deadline is not fill on this element, the system displays the largest of its "
                        u"possible children")
                ret.append(
                    PseudoMessage(
                        msg_type="significant",
                        text=richtextval(msg),
                        hidden_uid=generate_uid(),
                        can_hide=False,
                    )
                )
        if self.context.portal_type == "pstsubaction":
            if self.context.planned_end_date:
                max_children_deadline = find_max_deadline_on_children(
                    self.context,
                    {
                        "pstsubaction": "planned_end_date",
                        "subaction_link": "planned_end_date",
                        "task": "due_date"
                    }
                )
                if max_children_deadline:
                    if max_children_deadline > self.context.planned_end_date:
                        msg = _(u"The deadline of any one of children is greater than those of this element")
                        ret.append(
                            PseudoMessage(
                                msg_type="significant",
                                text=richtextval(msg),
                                hidden_uid=generate_uid(),
                                can_hide=False,
                            )
                        )
                if is_smaller_deadline_on_parents(self.context,
                                                  {"pstsubaction": "planned_end_date", "pstaction": "planned_end_date",
                                                   "operationalobjective": "planned_end_date"}):
                    msg = _(u"The deadline of this element is greater than one of its parents")
                    ret.append(
                        PseudoMessage(
                            msg_type="significant",
                            text=richtextval(msg),
                            hidden_uid=generate_uid(),
                            can_hide=False,
                        )
                    )
            else:
                msg = _(u"The deadline is not fill on this element, the system displays the largest of its "
                        u"possible children")
                ret.append(
                    PseudoMessage(
                        msg_type="significant",
                        text=richtextval(msg),
                        hidden_uid=generate_uid(),
                        can_hide=False,
                    )
                )
        if self.context.portal_type == "task":
            if self.context.due_date:
                max_children_deadline = find_max_deadline_on_children(
                    self.context,
                    {
                        "pstsubaction": "planned_end_date",
                        "subaction_link": "planned_end_date",
                        "task": "due_date"
                    }
                )
                if is_smaller_deadline_on_parents(self.context, {"task": "due_date", "pstsubaction": "planned_end_date",
                                                                 "pstaction": "planned_end_date",
                                                                 "operationalobjective": "planned_end_date"}):
                    msg = _(u"The deadline of this element is greater than one of its parents")
                    ret.append(
                        PseudoMessage(
                            msg_type="significant",
                            text=richtextval(msg),
                            hidden_uid=generate_uid(),
                            can_hide=False,
                        )
                    )
            else:
                msg = _(u"The deadline is not fill on this element")
                ret.append(
                    PseudoMessage(
                        msg_type="significant",
                        text=richtextval(msg),
                        hidden_uid=generate_uid(),
                        can_hide=False,
                    )
                )
        return ret


class SitemapLinkViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/sitemap_link.pt')

    def href(self):
        pst = getProjectSpace(self.context)
        if IProject.providedBy(self.context):  # TODO: test if context is descendant of pst ?
            return "{0}/sitemap?came_from={1}".format(
                pst.absolute_url(),
                self.context.UID(),
            )
        else:
            return "{0}/sitemap".format(
                pst.absolute_url(),
            )
