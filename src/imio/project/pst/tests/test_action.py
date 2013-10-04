# -*- coding: utf-8 -*-
""" Content action tests for this package."""

from imio.project.pst.testing import IntegrationTestCase, BaseTestCase
from imio.project.pst.content import action


class TestAction(IntegrationTestCase, BaseTestCase):
    """Test installation of imio.project.pst into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestAction, self).setUp()
        self.addUsers()
        self.addObjects()

    def test_default_manager(self):
        """
            test default values
        """
        oo = self.pst['os1']['oo1-1']
        act = oo['a1-1-1']

        class Dummy(object):
            def __init__(self, context):
                self.context = context

        # we login as a pst editor
        self.login('psteditor')
        self.assertEquals(action.default_manager(Dummy(oo)), [])
        # we login as a service member
        self.login('personnel')
        self.assertEquals(action.default_manager(Dummy(oo)), ['%s_actioneditor' % self.services['personnel'].UID()])
        # we login as a service member, the context isn't the good one
        self.login('personnel')
        self.assertEquals(action.default_manager(Dummy(act)), [])
