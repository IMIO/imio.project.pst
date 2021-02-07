# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor adds operational objective."""
    browser.open(context.absolute_url() + '/++add++operationalobjective')


def step_3a(browser):
    """The actor cancel the form."""
    form = browser.forms['form']
    form.find_button_by_label('Annuler').click()


def step_3c(browser):
    """The actor fills in the fields but omit mandatory fields and save."""
    form = browser.forms['form']
    form.find_button_by_label('Sauvegarder').click()


class TestCreateOperationalObjective(FunctionalTestCase):
    """Use case tests.
    Name: Create an operational objective
    Actor(s): pst admin, pst editors
    Goal: allows actors to create an operational objective
    Author: Franck Ngaha
    Created: 15/10/2020
    Updated: 25/01/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a strategic objective in anyone of all his states (created, ongoing, achieved)
    - a pst editor in the context of a strategic objective in anyone of all his states (created, ongoing, achieved)
    """

    def setUp(self):
        super(TestCreateOperationalObjective, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        # Contexts
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_1 = self.pst['etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient']
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'alternative_scenario_3b',
            'exceptional_scenario_3c'
        ]

    @browsing
    def test_scenarios_as_admin_in_strategic_objective_created(self, browser):
        api.content.transition(obj=self.os_1, transition='back_to_created')
        state = api.content.get_state(obj=self.os_1)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.os_1)

    @browsing
    def test_scenarios_as_admin_in_strategic_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.os_1)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.os_1)

    @browsing
    def test_scenarios_as_admin_in_strategic_objective_achieved(self, browser):
        api.content.transition(obj=self.os_1, transition='achieve')
        state = api.content.get_state(obj=self.os_1)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_admin, self.os_1)

    @browsing
    def test_scenarios_as_pst_editor_in_strategic_objective_created(self, browser):
        api.content.transition(obj=self.os_1, transition='back_to_created')
        state = api.content.get_state(obj=self.os_1)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_editor, self.os_1)

    @browsing
    def test_scenarios_as_pst_editor_in_strategic_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.os_1)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.os_1)

    @browsing
    def test_scenarios_as_pst_editor_in_strategic_objective_achieved(self, browser):
        api.content.transition(obj=self.os_1, transition='achieve')
        state = api.content.get_state(obj=self.os_1)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_editor, self.os_1)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor adds operational objective
        self.step_2(browser, context)  # The system calculates default values and displays the form
        self.step_3(browser)  # The actor fills in fields and save
        self.step_4(browser)  # The system creates and displays the operational objective

    def alternative_scenario_3a(self, browser, actor, context):
        """The actor cancels the form."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser, context)
        step_3a(browser)  # The actor cancels the form
        self.step_4a(browser, context)  # The system back to the previous page with "Addition canceled" Info

    def alternative_scenario_3b(self, browser, actor, context):
        """The actor fills in the fields but not the deadline and save."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser, context)
        self.step_3b(browser)  # The actor fills in the fields but not the deadline
        self.step_4b(browser)  # The system creates the operational objective with warning message

    def exceptional_scenario_3c(self, browser, actor, context):
        """The actor fills in the fields but omit a mandatory field and save."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser, context)
        step_3c(browser)  # The actor fills in the fields but omit mandatory fields
        self.step_4c(browser)  # system warn, (back to the step 2)

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser, context):
        """
        The system calculates the default values of the 'Categories' and 'Plans' fields,
        pre-populates and displays add action form
        """
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Objectif opérationnel', heading.text)
        form = browser.forms['form']
        fields = form.values
        categories = fields[self.categories_form_widget_name]
        plans = fields[self.plan_form_widget_name]
        self.assertTrue(categories.__eq__(set(getattr(context, 'categories', []))))
        self.assertTrue(plans.__eq__(set(getattr(context, 'plan', []))))

    def step_3(self, browser):
        """The actor fills in the form and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_dublinCore_form_widget_name] = u"Titre"
        fields[self.description_rich_form_widget_name] = u"Description"
        fields[self.result_indicator_label_form_widget_name] = u"Libellé"
        fields[self.result_indicator_value_form_widget_name] = u"100"
        fields[self.result_indicator_reached_value_form_widget_name] = u"50"
        fields[self.result_indicator_year_form_widget_name] = u"2020"
        fields[self.priority_form_widget_name] = u"2"
        fields[self.planned_end_date_day_form_widget_name] = u"31"
        fields[self.planned_end_date_month_form_widget_name] = u"12"
        fields[self.planned_end_date_year_form_widget_name] = u"2020"
        fields[self.representative_responsible_form_widget_name] = [self.echevins_config['bourgmestre']]
        fields[self.administrative_responsible_form_widget_name] = [
            self.services_config['service-informatique'].decode('utf8')]
        fields[self.manager_form_widget_name] = [self.services_config['service-informatique'].decode('utf8')]
        fields[self.extra_concerned_people_form_widget_name] = u"Partenaires externes"
        fields[self.budget_type_form_widget_name] = u"wallonie"
        fields[self.budget_year_form_widget_name] = u"2021"
        fields[self.budget_amount_form_widget_name] = u"10000,0"
        fields[self.budget_comments_form_widget_name] = u"Commentaires sur le financement/budget"
        fields[self.sdgs_form_widget_name] = [u"11"]
        fields[self.observation_form_widget_name] = u"Constat"
        fields[self.comments_form_widget_name] = u"Commentaires"
        form.find_button_by_label('Sauvegarder').click()

    def step_3b(self, browser):
        """The actor fills in the fields but not the deadline and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_dublinCore_form_widget_name] = u"Titre"
        fields[self.representative_responsible_form_widget_name] = [self.echevins_config['bourgmestre']]
        fields[self.administrative_responsible_form_widget_name] = [
            self.services_config['service-informatique'].decode('utf8')]
        fields[self.manager_form_widget_name] = [self.services_config['service-informatique'].decode('utf8')]
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser):
        """The system creates and displays the element with "Saved changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (OO.24)', heading.text)
        statusmessages.assert_message(u'Elément créé')

    def step_4a(self, browser, context):
        """The system back to the previous page with "Addition canceled" Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u"Ajout annulé")

    def step_4b(self, browser):
        """The system creates the pst action with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (OO.25)', heading.text)
        statusmessages.assert_message(u"Elément créé")

    def step_4c(self, browser):
        """The system displays warnings, (Back to the step 2)."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Objectif opérationnel', heading.text)
        self.assertTrue('Champ obligatoire' in browser.contents)
        statusmessages.assert_message(u"Il y a des erreurs.")
