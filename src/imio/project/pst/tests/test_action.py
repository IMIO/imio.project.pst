# -*- coding: utf-8 -*-
""" Content action tests for this package."""

from imio.project.pst.testing import FunctionalTestCase


class TestAction(FunctionalTestCase):
    """Test installation of imio.project.pst into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestAction, self).setUp()

    def test_setup(self):
        """ Test the setup """
        self.assertIn('pst', self.portal.objectIds())
