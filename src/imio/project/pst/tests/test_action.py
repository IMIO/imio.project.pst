# -*- coding: utf-8 -*-
""" Content action tests for this package."""
from datetime import datetime

from imio.project.pst.content import action
from imio.project.pst.content.pstprojectspace import PSTACTION_EXCLUDED_FIELDS
from imio.project.pst.testing import IntegrationTestCase
from imio.project.pst.utils import find_deadlines_on_children, find_max_deadline_on_children, find_brains_on_parents, \
    find_deadlines_on_parents, find_max_deadline_on_parents
from plone import api
from plone.app.testing import TEST_USER_NAME
from zope.app.content import queryContentType
from zope.interface import Invalid
from zope.schema import getFieldsInOrder
from zope.schema._bootstrapinterfaces import RequiredMissing
from zope.schema._bootstrapinterfaces import TooShort


class TestAction(IntegrationTestCase):
    """Test action.py."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestAction, self).setUp()
        self.os_10 = self.pst['etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-'
                              'de-serre-afin-dassurer-le-developpement-durable']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']
        self.a_16 = self.oo_15['reduire-la-consommation-energetique-de-ladministration-communale']
        self.sa_17 = self.a_16['realiser-un-audit-energetique-du-batiment']

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
        with self.assertRaises(RequiredMissing) as raised:  # field required
            validator.validate(None)
        with self.assertRaises(TooShort) as raised:  # field min_length
            validator.validate([])
        validator.validate([self.groups['service-proprete']])
        # bypass for pst editors
        self.login('psteditor')
        member = api.user.get_current()
        self.assertTrue('pst_editors' in member.getGroups())
        validator.validate([self.groups['service-proprete']])
        # constrain for service user
        self.login('agent')
        # with self.assertRaises(Invalid) as raised:
        #     validator.validate([])
        # self.assertEquals(raised.exception.message,
        #                   u'You must choose at least one group')
        with self.assertRaises(Invalid) as raised:
            validator.validate([self.groups[u'service-proprete']])
        self.assertEquals(raised.exception.message,
                          u'You must choose at least one group of which you are a member')
        validator.validate(self.groups.values())

    def test_pstaction_fields_type(self):
        """Test of fields type."""
        schema = queryContentType(self.ac1)
        fields = getFieldsInOrder(schema)
        # field is a tuple : (field_name, field_obj)
        for field in fields:
            try:
                # pstaction_fields_class is a dict : {'field_name': field_class}
                self.assertTrue(isinstance(field[1], self.pstaction_fields_class[field[0]]))
            except KeyError as err:
                # its ok for fields excluded intentionally
                print('EXCLUDED : {}'.format(err.message))
                if err.message in PSTACTION_EXCLUDED_FIELDS:
                    pass
