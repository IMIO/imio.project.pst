# -*- coding: utf-8 -*-
""" Content action tests for this package."""

from zope.interface import Invalid
from plone import api
from plone.app.testing import TEST_USER_NAME
from imio.project.pst.testing import IntegrationTestCase
from imio.project.pst.content import action


class TestAction(IntegrationTestCase):
    """Test action.py."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestAction, self).setUp()

    def test_default_manager(self):
        """
            test default values
        """

        class Dummy(object):
            def __init__(self, context):
                self.context = context

        # we login as a pst editor
        self.login('psteditor')
        self.assertEquals(action.default_manager(Dummy(self.oo1)), [])
        # we login as a service member
        self.login('agent')
        self.assertEquals(action.default_manager(Dummy(self.oo1)), [self.groups['service-population'],
                                                                    self.groups['service-etat-civil']])
        # we login as a service member, the context isn't the good one
        self.assertEquals(action.default_manager(Dummy(self.ac1)), [])

    def test_manager_validator(self):
        """
            test default values
        """
        validator = action.ManagerFieldValidator(self.ac1, None, None,
                                                 action.IPSTAction['manager'], None)
        # bypass for Managers
        self.login(TEST_USER_NAME)
        api.group.remove_user(groupname='%s_actioneditor' % self.groups['service-proprete'], username='agent')
        member = api.user.get_current()
        self.assertTrue(member.has_role('Manager'))
        validator.validate([])
        validator.validate([self.groups['service-proprete']])
        # bypass for pst editors
        self.login('psteditor')
        member = api.user.get_current()
        self.assertTrue('pst_editors' in member.getGroups())
        validator.validate([self.groups['service-proprete']])
        # constrain for service user
        self.login('agent')
        with self.assertRaises(Invalid) as raised:
            validator.validate([])
        self.assertEquals(raised.exception.message,
                          u'You must choose at least one group')
        with self.assertRaises(Invalid) as raised:
            validator.validate([self.groups[u'service-proprete']])
        self.assertEquals(raised.exception.message,
                          u'You must choose at least one group of which you are a member')
        validator.validate(self.groups.values())
