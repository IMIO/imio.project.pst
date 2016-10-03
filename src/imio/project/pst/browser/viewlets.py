# -*- coding: utf-8 -*-
"""Custom viewlets."""

from collective.task.browser.viewlets import TasksListViewlet as OriginalTasksListViewlet


class TasksListViewlet(OriginalTasksListViewlet):

    """Tasks list for current task container object."""

    def render(self):
        if self.context.portal_type in ('task', ):
            return super(TasksListViewlet, self).render()
        else:
            return ""
