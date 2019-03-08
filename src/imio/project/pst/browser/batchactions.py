# -*- coding: utf-8 -*-
"""Batch actions views."""

from collective.contact.plonegroup.utils import get_selected_org_suffix_users
from collective.task.browser.batchactions import AssignedGroupBatchActionForm as agbaf
from collective.task.browser.batchactions import AssignedUserBatchActionForm as aubaf
from imio.project.pst import ASSIGNED_USER_FUNCTIONS


class AssignedGroupBatchActionForm(agbaf):

    def get_group_users(self, assigned_group):
        return get_selected_org_suffix_users(assigned_group, ASSIGNED_USER_FUNCTIONS)


class AssignedUserBatchActionForm(aubaf):

    def get_group_users(self, assigned_group):
        return get_selected_org_suffix_users(assigned_group, ASSIGNED_USER_FUNCTIONS)
