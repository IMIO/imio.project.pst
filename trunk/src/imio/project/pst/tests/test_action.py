# -*- coding: utf-8 -*-
""" Content action tests for this package."""

from zope.interface import Invalid
from plone.app.testing import TEST_USER_NAME
from imio.project.pst.testing import IntegrationTestCase
from imio.project.pst.content import action


class TestAction(IntegrationTestCase):
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
        self.assertEquals(action.default_manager(Dummy(oo)), [self.groups['Personnel']])
        # we login as a service member, the context isn't the good one
        self.login('personnel')
        self.assertEquals(action.default_manager(Dummy(act)), [])

    def test_manager_validator(self):
        """
            test default values
        """
        oo = self.pst['os1']['oo1-1']
        act = oo['a1-1-1']
        validator = action.ManagerFieldValidator(act, None, None,
                                                 action.IPSTAction['manager'], None)
        # bypass for Managers
        self.login(TEST_USER_NAME)
        member = self.portal.portal_membership.getAuthenticatedMember()
        self.assertTrue(member.has_role('Manager'))
        validator.validate([])
        validator.validate([self.groups['Compta']])
        # bypass for pst editors
        self.login('psteditor')
        member = self.portal.portal_membership.getAuthenticatedMember()
        self.assertTrue('pst_editors' in member.getGroups())
        validator.validate([self.groups['Compta']])
        # constrain for service user
        self.login('personnel')
        with self.assertRaises(Invalid) as raised:
            validator.validate([])
        self.assertEquals(raised.exception.message,
                          u'You must choose at least one group')
        with self.assertRaises(Invalid) as raised:
            validator.validate([self.groups[u'Compta']])
        self.assertEquals(raised.exception.message,
                          u'You must choose at least one group of which you are a member')
        validator.validate(self.groups.values())

