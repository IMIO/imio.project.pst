# -*- coding: utf-8 -*-
"""Base module for unittesting."""

import unittest2
from Testing import ZopeTestCase as ztc
from Products.CMFPlone.utils import _createObjectByType
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import z2

import imio.project.pst


class PSTLayer(PloneWithPackageLayer):

    def setUpPloneSite(self, portal):
        _createObjectByType('Document', portal, id='front-page')
        portal.setDefaultPage('front-page')
        super(PSTLayer, self).setUpPloneSite(portal)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.portal_setup.runAllImportStepsFromProfile('profile-imio.project.pst:demo')

    def setUpZope(self, app, configurationContext):
        ztc.utils.setupCoreSessions(app)
        super(PSTLayer, self).setUpZope(app, configurationContext)


PST_TESTING_PROFILE = PSTLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.project.pst,
    additional_z2_products=('Products.PasswordStrength', 'imio.dashboard', 'imio.project.pst'),
    gs_profile_id='imio.project.pst:testing',
    name="PST_TESTS_PROFILE")

PST_TESTING_PROFILE_INTEGRATION = IntegrationTesting(
    bases=(PST_TESTING_PROFILE,), name="PST_TESTING_PROFILE_INTEGRATION")

PST_TEST_PROFILE_FUNCTIONAL = FunctionalTesting(
    bases=(PST_TESTING_PROFILE,), name="PST_TESTING_PROFILE_FUNCTIONAL")

PST_ROBOT_TESTING = FunctionalTesting(
    bases=(PST_TESTING_PROFILE,
           REMOTE_LIBRARY_BUNDLE_FIXTURE,
           z2.ZSERVER_FIXTURE,),
    name="PST_ROBOT_TESTING")


class IntegrationTestCase(unittest2.TestCase):
    """Base class for integration tests."""

    layer = PST_TESTING_PROFILE_INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os1 = self.pst['etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient']
        self.oo1 = self.os1['diminuer-le-temps-dattente-de-lusager-au-guichet-population-de-20-dans-les-12-mois'
                            '-a-venir']
        self.ac1 = self.oo1['engager-2-agents-pour-le-service-population']
        act_srv = [u'cellule-marches-publics', u'secretariat-communal', u'service-etat-civil', u'service-informatique',
                   u'service-proprete', u'service-population', u'service-travaux', u'service-de-lurbanisme']
        srv_obj = self.portal['contacts']['plonegroup-organization']['services']
        self.groups = dict([(srv, srv_obj[srv].UID().decode('utf8')) for srv in act_srv])

    def login(self, username):
        logout()
        login(self.portal, username)


class FunctionalTestCase(unittest2.TestCase):
    """Base class for functional tests."""

    layer = PST_TEST_PROFILE_FUNCTIONAL

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.portal = self.layer['portal']
