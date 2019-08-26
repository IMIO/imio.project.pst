# -*- coding: utf-8 -*-
"""Custom viewlets."""

from collective.task.browser.viewlets import TasksListViewlet as OriginalTasksListViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase


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


class ActionLinkForActionViewlet(ViewletBase):

    index = ViewPageTemplateFile('actionlinkforaction.pt')

    def action_link(self):
        return self.context.back_references()

    # TODO: Show OO for action_link
