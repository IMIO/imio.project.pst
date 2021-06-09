# -*- coding: utf-8 -*-
""" data.py tests for this package."""

from imio.project.pst.testing import IntegrationTestCase


class TestData(IntegrationTestCase):
    """Test data.py."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestData, self).setUp()

    def test_styles_templates(self):
        self.assertEquals(
            self.portal.templates.objectIds(),
            [
                'style', 'style_wo_nb', 'detail', 'detail-tasks', 'follow', 'follow-tasks', 'export', 'detail-all',
                'detail-tasks-all', 'ddetail', 'ddetail-tasks', 'dfollow', 'dfollow-tasks', 'dexport', 'ddetail-all',
                'ddetail-tasks-all', 'follow-all', 'follow-tasks-all', 'dfollow-all', 'dfollow-tasks-all', 'managers',
                'dmanagers', 'editors', 'deditors',
            ]
        )
