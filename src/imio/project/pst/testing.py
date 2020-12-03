# -*- coding: utf-8 -*-
"""Base module for unittesting."""

import os
import unittest

import imio.project.pst
from dexterity.localrolesfield.field import LocalRolesField
from imio.project.pst.setuphandlers import PASSWORD
from imio.project.pst.utils import get_echevins_config
from imio.project.pst.utils import get_services_config
from imio.pyutils.system import runCommand
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield import RichText
from plone.testing import z2
from plone.testing.z2 import Browser
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Testing import ZopeTestCase as ztc
from zope.globalrequest.local import setLocal
from zope.schema import Choice
from zope.schema import Date
from zope.schema import Int
from zope.schema import List
from zope.schema import Text


class PSTLayer(PloneWithPackageLayer):

    def setUpPloneSite(self, portal):
        setattr(portal, '_TESTING_SITE_', True)
        setLocal('request', portal.REQUEST)
        applyProfile(portal, 'Products.CMFPlone:plone')
        #        applyProfile(portal, 'Products.CMFPlone:plone-content')  # could be done too
        manage_addExternalMethod(portal, 'lock-unlock', '', 'imio.project.pst.robot', 'lock')
        manage_addExternalMethod(portal, 'robot_init', '', 'imio.project.pst.robot', 'robot_init')

        super(PSTLayer, self).setUpPloneSite(portal)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.portal_setup.runAllImportStepsFromProfile('profile-imio.project.pst:demo')

    def setUpZope(self, app, configurationContext):
        ztc.utils.setupCoreSessions(app)
        super(PSTLayer, self).setUpZope(app, configurationContext)
        (stdout, stderr, st) = runCommand('%s/bin/soffice.sh restart' % os.getenv('PWD'))

    def tearDownZope(self, app):
        """Tear down Zope."""
        (stdout, stderr, st) = runCommand('%s/bin/soffice.sh stop' % os.getenv('PWD'))


PST_TESTING_PROFILE = PSTLayer(
    zcml_filename="testing.zcml",
    zcml_package=imio.project.pst,
    additional_z2_products=('Products.PasswordStrength', 'Products.DateRecurringIndex', 'imio.dashboard',
                            'imio.project.pst'),
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


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = PST_TESTING_PROFILE_INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()

        # default setup
        self.os_fields = [
            {'read_tal_condition': '', 'field_name': 'IDublinCore.title', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'description_rich', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'reference_number', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'categories', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'plan', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'IAnalyticBudget.projection', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'IAnalyticBudget.analytic_budget', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'budget', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'budget_comments', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'observation', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'comments', 'write_tal_condition': ''}
        ]
        self.oo_fields = [
            {'read_tal_condition': '', 'field_name': 'IDublinCore.title', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'description_rich', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'reference_number', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'categories', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'plan', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'result_indicator', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'priority', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'planned_end_date', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'representative_responsible', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'administrative_responsible', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'manager', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'extra_concerned_people', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'IAnalyticBudget.projection', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'IAnalyticBudget.analytic_budget', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'budget', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'budget_comments', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'ISustainableDevelopmentGoals.sdgs', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'observation', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'comments', 'write_tal_condition': ''}
        ]

        self.a_fields = [
            {'read_tal_condition': '', 'field_name': 'IDublinCore.title', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'description_rich', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'reference_number', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'categories', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'plan', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'result_indicator', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'planned_end_date', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'planned_begin_date', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'effective_begin_date', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'effective_end_date', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'progress', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'health_indicator', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'health_indicator_details', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'representative_responsible', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'manager', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'responsible', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'extra_concerned_people', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'IAnalyticBudget.projection', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'IAnalyticBudget.analytic_budget', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'budget', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'budget_comments', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'ISustainableDevelopmentGoals.sdgs', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'observation', 'write_tal_condition': ''},
            {'read_tal_condition': '', 'field_name': 'comments', 'write_tal_condition': ''}
        ]

        self.os_columns = [
            u'select_row', u'pretty_link', u'review_state', u'categories', u'ModificationDate', u'history_actions'
        ]
        self.oo_columns = [
            u'select_row', u'pretty_link', u'parents', u'review_state', u'manager', u'planned_end_date', u'priority',
            u'categories', u'sdgs', u'ModificationDate', u'history_actions'
        ]
        self.a_columns = [
            u'select_row', u'pretty_link', u'parents', u'review_state', u'manager', u'responsible',
            u'planned_begin_date', u'planned_end_date', u'effective_begin_date', u'effective_end_date', u'progress',
            u'health_indicator', u'sdgs', u'ModificationDate', u'history_actions'
        ]
        self.so_bdg_states = ['ongoing', 'achieved']
        self.oo_bdg_states = ['ongoing', 'achieved']
        self.a_bdg_states = ['ongoing', 'terminated', 'to_be_scheduled']

        # tests setup
        self.strategicobjective_fields_class = {
            'description_rich': RichText,
            'reference_number': Int,
            'categories': List,
            'budget': List,
            'budget_comments': RichText,
            'effective_end_date': Date,
            'observation': RichText,
            'comments': RichText,
            'plan': List,
        }
        self.operationalobjective_fields_class = {
            'description_rich': RichText,
            'reference_number': Int,
            'categories': List,
            'priority': Choice,
            'budget': List,
            'budget_comments': RichText,
            'manager': LocalRolesField,
            'extra_concerned_people': Text,
            'result_indicator': List,
            'planned_end_date': Date,
            'observation': RichText,
            'comments': RichText,
            'plan': List,
            'representative_responsible': LocalRolesField,
            'administrative_responsible': LocalRolesField,
            'manager': LocalRolesField,
        }
        self.pstaction_fields_class = {
            'description_rich': RichText,
            'reference_number': Int,
            'categories': List,
            'budget': List,
            'budget_comments': RichText,
            'manager': LocalRolesField,
            'extra_concerned_people': Text,
            'result_indicator': List,
            'planned_begin_date': Date,
            'effective_begin_date': Date,
            'planned_end_date': Date,
            'effective_end_date': Date,
            'progress': Int,
            'observation': RichText,
            'comments': RichText,
            'plan': List,
            'representative_responsible': LocalRolesField,
            'responsible': Choice,
            'health_indicator': Choice,
            'health_indicator_details': Text,
        }

        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os1 = self.pst['etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient']
        self.oo1 = self.os1['diminuer-le-temps-dattente-de-lusager-au-guichet-population-de-20-dans-les-12-mois'
                            '-a-venir']
        self.ac1 = self.oo1['engager-2-agents-pour-le-service-population']
        self.tk1 = self.ac1['ajouter-une-annonce-sur-le-site-internet']
        act_srv = [u'cellule-marches-publics', u'secretariat-communal', u'service-etat-civil', u'service-informatique',
                   u'service-proprete', u'service-population', u'service-travaux', u'service-de-lurbanisme']
        srv_obj = self.portal['contacts']['plonegroup-organization']['services']
        self.groups = dict([(srv, srv_obj[srv].UID().decode('utf8')) for srv in act_srv])

    def login(self, username):
        logout()
        login(self.portal, username)


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = PST_TEST_PROFILE_FUNCTIONAL

    def setUp(self):
        super(FunctionalTestCase, self).setUp()

        # resources setup
        self.app = self.layer['app']
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.browser = Browser(self.portal)

        # param setup
        self.password = PASSWORD
        self.echevins_config = get_echevins_config(self.portal)
        self.services_config = get_services_config()
        self.title_form_widget_name = 'form.widgets.IDublinCore.title'
        self.description_form_widget_name = 'form.widgets.description_rich'
        self.categories_form_widget_name = 'form.widgets.categories:list'
        self.plan_form_widget_name = 'form.widgets.plan:list'
        self.result_indicator_label_form_widget_name = 'form.widgets.result_indicator.TT.widgets.label'
        self.result_indicator_value_form_widget_name = 'form.widgets.result_indicator.TT.widgets.value'
        self.result_indicator_reached_value_form_widget_name = 'form.widgets.result_indicator.TT.widgets.reached_value'
        self.result_indicator_year_form_widget_name = 'form.widgets.result_indicator.TT.widgets.year:list'
        self.priority_form_widget_name = 'form.widgets.priority:list'
        self.planned_end_date_day_form_widget_name = 'form.widgets.planned_end_date-day'
        self.planned_end_date_month_form_widget_name = 'form.widgets.planned_end_date-month'
        self.planned_end_date_year_form_widget_name = 'form.widgets.planned_end_date-year'
        self.planned_begin_date_day_form_widget_name = 'form.widgets.planned_begin_date-day'
        self.planned_begin_date_month_form_widget_name = 'form.widgets.planned_begin_date-month'
        self.planned_begin_date_year_form_widget_name = 'form.widgets.planned_begin_date-year'
        self.effective_begin_date_day_form_widget_name = 'form.widgets.effective_begin_date-day'
        self.effective_begin_date_month_form_widget_name = 'form.widgets.effective_begin_date-month'
        self.effective_begin_date_year_form_widget_name = 'form.widgets.effective_begin_date-year'
        self.effective_end_date_day_form_widget_name = 'form.widgets.effective_end_date-day'
        self.effective_end_date_month_form_widget_name = 'form.widgets.effective_end_date-month'
        self.effective_end_date_year_form_widget_name = 'form.widgets.effective_end_date-year'
        self.progress_form_widget_name = 'form.widgets.progress'
        self.health_indicator_form_widget_name = 'form.widgets.health_indicator:list'
        self.health_indicator_details = 'form.widgets.health_indicator_details'
        self.representative_responsible_form_widget_name = 'form.widgets.representative_responsible:list'
        self.administrative_responsible_form_widget_name = 'form.widgets.administrative_responsible:list'
        self.manager_form_widget_name = 'form.widgets.manager:list'
        self.responsible_form_widget_name = 'form.widgets.responsible:list'
        self.extra_concerned_people_form_widget_name = 'form.widgets.extra_concerned_people'
        self.budget_type_form_widget_name = 'form.widgets.budget.TT.widgets.budget_type:list'
        self.budget_year_form_widget_name = 'form.widgets.budget.TT.widgets.year:list'
        self.budget_amount_form_widget_name = 'form.widgets.budget.TT.widgets.amount'
        self.budget_comments_form_widget_name = 'form.widgets.budget_comments'
        self.sdgs_form_widget_name = 'form.widgets.ISustainableDevelopmentGoals.sdgs:list'
        self.observation_form_widget_name = 'form.widgets.observation'
        self.comments_form_widget_name = 'form.widgets.comments'
        self.save_button_name = 'form.buttons.save'
        self.cancel_button_name = 'form.buttons.cancel'

    def login(self, username, password):
        """Simulate logging in via the login form."""
        self.browser.open(self.portal.absolute_url() + "/login_form")
        self.browser.getControl(name='__ac_name').value = username
        self.browser.getControl(name='__ac_password').value = password
        self.browser.getControl(name='submit').click()
        self.assertTrue("Votre session est maintenant ouverte" in self.browser.contents)

    def logout(self):
        """Logout with testBrowser."""
        self.browser.open(self.portal.absolute_url() + '/logout')
        self.assertTrue("Votre session est maintenant termin\xc3\xa9" in self.browser.contents)
