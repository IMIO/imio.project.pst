# -*- coding: utf-8 -*-
"""Base module for unittesting."""

import unittest2
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting

import imio.project.pst


PST_TESTING_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.project.pst,
    additional_z2_products=('imio.project.pst', ),
    gs_profile_id='imio.project.pst:testing',
    name="PST_TESTS_PROFILE")

PST_TESTING_PROFILE_INTEGRATION = IntegrationTesting(
    bases=(PST_TESTING_PROFILE,), name="PST_TESTING_PROFILE_INTEGRATION")

PST_TEST_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(PST_TESTING_PROFILE,), name="PST_TESTING_PROFILE_FUNCTIONAL")


class IntegrationTestCase(unittest2.TestCase):
    """Base class for integration tests."""

    layer = PST_TESTING_PROFILE_INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']


class FunctionalTestCase(unittest2.TestCase):
    """Base class for functional tests."""

    layer = PST_TEST_PROFILE_FUNCTIONAL