# -*- coding: utf-8 -*-
""" adapters.py tests for this package."""

from imio.project.pst.testing import IntegrationTestCase
from ..adapters import (
    UserIsAdministrativeResponsibleCriterion, UserIsActionEditorCriterion, TaskInAssignedGroupCriterion
)


class TestAdapters(IntegrationTestCase):
    """Test installation of imio.project.pst into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestAdapters, self).setUp()
        self.addUsers()
        self.addObjects()

    def test_UserIsAdministrativeResponsibleCriterion(self):
        crit = UserIsAdministrativeResponsibleCriterion(self.portal)
        self.login('personnel-admin_resp')
        self.assertDictEqual(crit.query, {'administrative_responsible': {'query': [self.groups['Personnel']]}})

    def test_UserIsActionEditorCriterion(self):
        crit = UserIsActionEditorCriterion(self.portal)
        self.login('personnel-actioneditor')
        self.assertDictEqual(crit.query, {'manager': {'query': [self.groups['Personnel']]}})

    def test_TaskInAssignedGroupCriterion(self):
        crit = TaskInAssignedGroupCriterion(self.portal)
        self.login('personnel-actioneditor')
        self.assertDictEqual(crit.query, {'assigned_group': {'query': [self.groups['Personnel']]}})
