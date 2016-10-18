# -*- coding: utf-8 -*-
""" adapters.py tests for this package."""

from plone import api

from imio.project.pst.testing import IntegrationTestCase
from ..adapters import (
    UserIsAdministrativeResponsibleCriterion, UserIsActionEditorCriterion, TaskInAssignedGroupCriterion,
    ChildrenActionDeadlineHasPassedCriterion
)


class TestAdapters(IntegrationTestCase):
    """Test installation of imio.project.pst into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestAdapters, self).setUp()
        api.user.create('t@mio.be', 'imio', 'Project69!')

    def test_UserIsAdministrativeResponsibleCriterion(self):
        crit = UserIsAdministrativeResponsibleCriterion(self.portal)
        self.login('imio')
        api.group.add_user(groupname='%s_admin_resp' % self.groups['service-proprete'], username='imio')
        self.assertDictEqual(crit.query, {'administrative_responsible': {'query': [self.groups['service-proprete']]}})

    def test_UserIsActionEditorCriterion(self):
        crit = UserIsActionEditorCriterion(self.portal)
        self.login('imio')
        api.group.add_user(groupname='%s_actioneditor' % self.groups['service-proprete'], username='imio')
        self.assertDictEqual(crit.query, {'manager': {'query': [self.groups['service-proprete']]}})

    def test_TaskInAssignedGroupCriterion(self):
        crit = TaskInAssignedGroupCriterion(self.portal)
        self.login('imio')
        api.group.add_user(groupname='%s_actioneditor' % self.groups['service-proprete'], username='imio')
        self.assertDictEqual(crit.query, {'assigned_group': {'query': [self.groups['service-proprete']]}})

    def test_ChildrenActionDeadlineHasPassedCriterion(self):
        crit = ChildrenActionDeadlineHasPassedCriterion(self.portal)
        self.login('agent')
        dic = crit.query
        self.assertIn(':has_child', dic)
        self.assertIn('portal_type', dic[':has_child']['query'])
        self.assertIn('planned_end_date', dic[':has_child']['query'])
        self.assertIn('sort_order', dic[':has_child']['query'])
        self.assertIn('sort_on', dic[':has_child']['query'])
