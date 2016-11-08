# -*- coding: utf-8 -*-
"""Customize task views."""

import copy
from z3c.form.interfaces import HIDDEN_MODE
from Products.CMFPlone.utils import base_hasattr
from plone import api
from plone.dexterity.browser.add import DefaultAddView, DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm

from collective.contact.plonegroup.utils import voc_selected_org_suffix_users
from collective.eeafaceted.z3ctable.columns import VocabularyColumn
from collective.task import _ as _t

from .. import _


def filter_task_assigned_users(group):
    """
        Filter assigned_user in dms incoming mail
    """
    return voc_selected_org_suffix_users(group, ['actioneditor', 'editeur', 'validateur'])


def TaskUpdateWidgets(self):
    # Override default vocabulary
    self.widgets['ITask.assigned_group'].field = copy.copy(self.widgets['ITask.assigned_group'].field)
    self.widgets['ITask.assigned_group'].field.slave_fields[0]['vocab_method'] = filter_task_assigned_users
    # Set assigned_group as required
    self.widgets['ITask.assigned_group'].required = True
    # Hide enquirer
    self.widgets['ITask.enquirer'].mode = HIDDEN_MODE


class TaskEdit(DefaultEditForm):
    """
      Edit view override of update
    """
    def updateWidgets(self):
        super(TaskEdit, self).updateWidgets()
        TaskUpdateWidgets(self)
        if not self.context.assigned_user \
                and api.content.get_state(obj=self.context) == 'to_assign':
            self.widgets['ITask.assigned_user'].field = copy.copy(self.widgets['ITask.assigned_user'].field)
            self.widgets['ITask.assigned_user'].field.description = \
                _t(u'You must select an assigned user before continuing !')


class CustomAddForm(DefaultAddForm):

    portal_type = 'task'

    def updateWidgets(self):
        super(CustomAddForm, self).updateWidgets()
        TaskUpdateWidgets(self)
        if base_hasattr(self.context, 'manager') and self.context.manager:
            self.widgets['ITask.assigned_group'].value = self.context.manager
        # Set current user as enquirer and hide it
        userid = api.user.get_current().getId()
        if userid != 'admin':
            self.widgets['ITask.enquirer'].value = userid


class Add(DefaultAddView):
    """
        Add form redefinition to customize fields.
    """
    form = CustomAddForm


class AssignedGroupColumn(VocabularyColumn):

    header = _("Assigned group")
    weight = 30
    attrName = 'manager'

    vocabulary = u'imio.project.core.content.project.manager_vocabulary'
