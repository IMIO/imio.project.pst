# -*- coding: utf-8 -*-
"""Customize task views."""
from Products.CMFPlone.utils import base_hasattr
from plone.dexterity.browser.add import DefaultAddView, DefaultAddForm


class CustomAddForm(DefaultAddForm):

    portal_type = 'task'

    def updateWidgets(self):
        super(CustomAddForm, self).updateWidgets()
        if base_hasattr(self.context, 'manager') and self.context.manager:
            self.widgets['ITask.assigned_group'].value = self.context.manager


class Add(DefaultAddView):
    """
        Add form redefinition to customize fields.
    """
    form = CustomAddForm
