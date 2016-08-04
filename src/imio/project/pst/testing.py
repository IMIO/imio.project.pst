# -*- coding: utf-8 -*-
"""Base module for unittesting."""

import unittest2
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login, logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from datetime import datetime
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.dexterity.utils import createContentInContainer
from collective.contact.plonegroup.config import ORGANIZATIONS_REGISTRY, PLONEGROUP_ORG
import imio.project.pst

PST_TESTING_PROFILE = PloneWithPackageLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.project.pst,
    additional_z2_products=('Products.PasswordStrength', 'imio.dashboard', 'imio.project.pst'),
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
        self.pst = self.portal['pst']

    def login(self, username):
        logout()
        login(self.portal, username)

    def addUsers(self):
        self.portal = self.layer['portal']
        # login as Manager
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        # add users
        self.portal.portal_registration.addMember(id="psteditor", password="Project69!")
        self.portal.acl_users.source_groups.addPrincipalToGroup("psteditor", "pst_editors")
        # add contacts, plone groups, users
        self.portal.contacts.invokeFactory('organization', id=PLONEGROUP_ORG)
        own_orga = self.portal.contacts[PLONEGROUP_ORG]
        createContentInContainer(own_orga, 'organization', **{'title': u'Services'})
        self.groups = {}
        registry = getUtility(IRegistry)
        for service in (u'Personnel', u'Compta'):
            obj = createContentInContainer(own_orga['services'], 'organization', **{'title': service})
            registry[ORGANIZATIONS_REGISTRY] = registry[ORGANIZATIONS_REGISTRY] + [obj.UID()]
            self.groups[service] = '%s_actioneditor' % obj.UID()
            user = service.lower()
            self.portal.portal_registration.addMember(id=user, password="Project69!")
            self.portal.acl_users.source_groups.addPrincipalToGroup(user, "%s_actioneditor" % obj.UID())
        logout()

    def addObjects(self):
        self.portal = self.layer['portal']
        # login as Manager
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        services = self.portal.contacts['plonegroup-organization']['services']
        data = {
            'os1':
            {
            'title': u'OS1',
            'categories': u'volet-externe-dvp-politiques-proprete-securite-publique',
            'budget': [],
            'budget_comments': u'',
            'operationalobjectives': [
                {
                    'title': u'OO1-1',
                    u'result_indicator': [{'value': 50, 'label': u'Nombre de sacs poubelles récoltés '
                                          u'chaque année et à l\'échéance (31 12 2015)',
                                          'reached_value': 0}],
                    'priority': u'1',
                    'planned_end_date': datetime.date(datetime(2015, 12, 31)),
                    'representative_responsible': [],
                    'administrative_responsible': [services['personnel'].UID()],
                    'manager': ['%s_actioneditor' % services['personnel'].UID()],
                    'extra_concerned_people': u'Police\r\nAgents constatateurs communaux\r\nAgent ',
                    'budget': [],
                    'budget_comments': u'Fonds propres (en cours de chiffrage)',
                    'comments': u'',
                    'actions': [
                        {'title': u'A1-1-1',
                         'manager': ['%s_actioneditor' % services['personnel'].UID()],
                         'planned_end_date': datetime.date(datetime(2014, 06, 30)),
                         'extra_concerned_people': u'La firme adjudicatrice au terme du marché public',
                         'budget': [{'amount': 12500.0, 'budget_type': 'wallonie', 'year': '2013'},
                                    ],
                         'budget_comments': u'1000 euros\r\nBudget ordinaire\r\nArticle budgétaire n°: ...',
                         'health_indicator': u'risque',
                         'health_indicator_details': u'Agent traitant malade pour minimum 3 mois -> risque de retard',
                         'work_plan': u'<p>Les principales tâches à réaliser dans un ordre logique sont:<p>'
                                      u'<ul>'
                                      u'<li>inventaire des parcs existants sur la commune (Maxime/Patrick)</li>'
                                      u'<li>passation d\'un marché public pour commander les distributeurs (Michèle) '
                                      u'finalisé pour le 01 09 2013</li>'
                                      u'<li>réception des distributeurs à l\'excution du marché (Michèle)</li>'
                                      u'<li>placement des distributeurs (Maxime/Patrick) pour le 01 12 2013</li>'
                                      u'<li>gestion des stocks de sachets (Michèle)</li>'
                                      u'<li>réapprovisionnement (Maxime)</li>'
                                      u'</ul>',
                         'comments': u'Attendre le placement des nouvelles poubelles (avant le 01 12 2013)'
                         },
                    ]
                },
            ],
            },
        }

        # create all this in a folder named 'pst' at the root of the Plone Site
        pst = self.portal.pst
        for strategicobjective in data:
            strategicObj = createContentInContainer(pst, "strategicobjective", id=strategicobjective,
                                                    **data[strategicobjective])
            for operationalobjective in data[strategicobjective]['operationalobjectives']:
                operationalObj = createContentInContainer(strategicObj, "operationalobjective", **operationalobjective)
                for action in operationalobjective['actions']:
                    createContentInContainer(operationalObj, "pstaction", **action)
        logout()


class FunctionalTestCase(unittest2.TestCase):
    """Base class for functional tests."""

    layer = PST_TEST_PROFILE_FUNCTIONAL

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.portal = self.layer['portal']
