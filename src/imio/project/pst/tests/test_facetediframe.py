# -*- coding: utf-8 -*-
""" facetediframe.py tests for this package."""

from collective.eeafaceted.dashboard.utils import getCriterionByTitle
from imio.project.pst.testing import IntegrationTestCase


class TestFacetediframe(IntegrationTestCase):
    """"""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestFacetediframe, self).setUp()

    def test_Criteria(self):
        # strategicobjectives search
        crit = getCriterionByTitle(self.pst['strategicobjectives'], 'Sort on')
        self.assertEquals(crit.default, 'getObjPositionInParent')
        self.assertIsNotNone(getCriterionByTitle(self.pst['strategicobjectives'], 'Categories'))
        self.assertIsNone(getCriterionByTitle(self.pst['strategicobjectives'], 'Priority'))
        # pst criteria
        crit = getCriterionByTitle(self.pst, 'Sort on')
        self.assertEquals(crit.default, 'getObjPositionInParent')
        self.assertIsNotNone(getCriterionByTitle(self.pst, 'Categories'))
        self.assertIsNone(getCriterionByTitle(self.pst, 'Priority'))
        self.assertIsNotNone(getCriterionByTitle(self.pst, 'path'))
        # oo search
        crit = getCriterionByTitle(self.pst['operationalobjectives'], 'Sort on')
        self.assertEquals(crit.default, 'sortable_title')
        self.assertIsNotNone(getCriterionByTitle(self.pst['operationalobjectives'], 'Priority'))
        # os criteria
        crit = getCriterionByTitle(self.os1, 'Sort on')
        self.assertEquals(crit.default, 'getObjPositionInParent')
        self.assertIsNotNone(getCriterionByTitle(self.os1, 'Priority'))
        self.assertIsNotNone(getCriterionByTitle(self.os1, 'path'))
        # actions search
        crit = getCriterionByTitle(self.pst['pstactions'], 'Sort on')
        self.assertEquals(crit.default, 'sortable_title')
        self.assertIsNotNone(getCriterionByTitle(self.pst['pstactions'], 'Health indicator'))
        # oo criteria
        crit = getCriterionByTitle(self.oo2, 'Sort on')
        self.assertEquals(crit.default, 'getObjPositionInParent')
        self.assertIsNotNone(getCriterionByTitle(self.oo2, 'Health indicator'))
        self.assertIsNotNone(getCriterionByTitle(self.oo2, 'path'))
        # tasks search
        crit = getCriterionByTitle(self.pst['tasks'], 'Sort on')
        self.assertEquals(crit.default, 'sortable_title')
        self.assertIsNotNone(getCriterionByTitle(self.pst['tasks'], 'Assigned group'))
        # action criteria
        crit = getCriterionByTitle(self.a3, 'Sort on')
        self.assertEquals(crit.default, 'getObjPositionInParent')
        self.assertIsNotNone(getCriterionByTitle(self.a3, 'Assigned group'))
        self.assertIsNotNone(getCriterionByTitle(self.a3, 'path'))
