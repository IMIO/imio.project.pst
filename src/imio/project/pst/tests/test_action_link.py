# -*- coding: utf-8 -*-
""" pstprojectspace.py tests for this package."""

from imio.project.pst.testing import IntegrationTestCase
from plone import api
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent


class TestActionLink(IntegrationTestCase):
    """Test action_link.py."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestActionLink, self).setUp()
        intids = getUtility(IIntIds)
        self.a24 = api.content.create(
            container=self.oo2,
            type='pstaction',
            id='pstaction-24',
            title='Pstaction 24',
            safe_id=False,
        )
        self.al24 = api.content.create(
            container=self.oo6,
            type='action_link',
            id='action-link-1',
            title='Action Link 1',
            safe_id=False,
            symbolic_link=RelationValue(intids.getId(self.a24))
        )

    def test_link(self):
        self.assertEqual(self.al4._link, self.a4)

    def test_title(self):
        self.assertEqual(self.al4.Title(), 'Créer un guichet supplémentaire dans les 3 mois (A.4)')

    def test_portal_type(self):
        self.assertEqual(self.al4.portal_type, 'pstaction')

    def test_symlink_status_index(self):
        pc = self.portal.portal_catalog
        self.assertEqual(len(pc(symlink_status='link')), 5)
        self.assertEqual(len(pc(symlink_status='source')), 4)
        self.assertEqual(len(pc(symlink_status='void')), 132)

    def test_of_indexing_when_source_modified(self):
        self.a24.title = "New title"
        notify(ObjectModifiedEvent(self.a24))
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog(reference_number=24)
        for brain in brains:
            self.assertEqual(brain.Title, 'New title (A.24)')
