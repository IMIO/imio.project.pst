# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor adds pst action."""
    browser.open(context.absolute_url() + '/++add++pstaction')


def step_3a(browser):
    """The actor cancels the form."""
    form = browser.forms['form']
    form.find_button_by_label('Annuler').click()


def step_3c(browser):
    """The actor fills in the fields but omit mandatory fields and save."""
    form = browser.forms['form']
    form.find_button_by_label('Sauvegarder').click()


class TestCreatePstAction(FunctionalTestCase):
    """Use case tests.
    Name: Create a pst action
    Actor(s): pst admin, pst editors, administrative responsible, manager
    Goal: allows actors to create a pst action
    Author: Franck Ngaha
    Created: 12/01/2021
    Updated: 24/02/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - a pst editor in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - an administrative responsible in the context of an operational objective in state ongoing
    - a manager in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    """

    def setUp(self):
        super(TestCreatePstAction, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.adm_resp = {'username': 'chef', 'password': self.password}
        self.manager = {'username': 'agent', 'password': self.password}
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'alternative_scenario_3b',
            'exceptional_scenario_3c',
            'alternative_scenario_3d',
        ]

    @browsing
    def test_scenarios_as_admin_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.oo2)

    @browsing
    def test_scenarios_as_admin_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.oo2)

    @browsing
    def test_main_scenario_as_admin_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo2, transition='achieve')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_admin, self.oo2)

    @browsing
    def test_scenarios_as_pst_editor_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_editor, self.oo2)

    @browsing
    def test_scenarios_as_pst_editor_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.oo2)

    @browsing
    def test_main_scenario_as_pst_editor_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo2, transition='achieve')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_editor, self.oo2)

    # TODO: Fix "InsufficientPrivileges" PRJ-471
    # @browsing
    # def test_scenarios_as_adm_resp_in_operational_objective_ongoing(self, browser):
    #     state = api.content.get_state(obj=self.oo2)
    #     self.assertEqual(state, 'ongoing')
    #     self.call_scenarios(browser, self.adm_resp, self.oo2)
    #
    @browsing
    def test_scenarios_as_manager_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.oo2)

    @browsing
    def test_scenarios_as_manager_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.oo2)

    @browsing
    def test_main_scenario_as_manager_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo2, transition='achieve')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.manager, self.oo2)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor adds pst action
        self.step_2(browser, context)  # The system calculates default values and displays the form
        self.step_3(browser)  # The actor fills in fields and save
        self.step_4(browser)  # The system creates and displays the pst action

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
        self.step_4b(browser)  # The system creates the pst action with warning message

    def exceptional_scenario_3c(self, browser, actor, context):
        """The actor fills in the fields but omit a mandatory field and save."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser, context)
        step_3c(browser)  # The actor fills in the fields but omit mandatory fields
        self.step_4c(browser)  # system warn, (back to the step 2)

    def alternative_scenario_3d(self, browser, actor, context):
        """The actor fills in element with a deadline date greater than one of the parents."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser, context)
        self.step_3d(browser)  # The actor fills in the fields with greater deadline
        self.step_4d(browser)  # The system creates the pst action with warning message

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
        self.assertEqual(u'Ajouter Action', heading.text)
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
        fields[self.planned_end_date_day_form_widget_name] = u"30"
        fields[self.planned_end_date_month_form_widget_name] = u"9"
        fields[self.planned_end_date_year_form_widget_name] = u"2020"
        fields[self.planned_begin_date_day_form_widget_name] = u"1"
        fields[self.planned_begin_date_month_form_widget_name] = u"1"
        fields[self.planned_begin_date_year_form_widget_name] = u"2020"
        fields[self.effective_begin_date_day_form_widget_name] = u"1"
        fields[self.effective_begin_date_month_form_widget_name] = u"1"
        fields[self.effective_begin_date_year_form_widget_name] = u"2020"
        fields[self.effective_end_date_day_form_widget_name] = u"30"
        fields[self.effective_end_date_month_form_widget_name] = u"9"
        fields[self.effective_end_date_year_form_widget_name] = u"2020"
        fields[self.progress_form_widget_name] = u"100"
        fields[self.health_indicator_form_widget_name] = u"bon"
        fields[self.health_indicator_details] = u"Détails de l'indice de santé"
        fields[self.representative_responsible_form_widget_name] = [self.echevins_config['bourgmestre']]
        fields[self.manager_form_widget_name] = [self.services_config['service-informatique'].decode('utf8')]
        fields[self.responsible_form_widget_name] = u'agent'
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
        fields[self.manager_form_widget_name] = [self.services_config['service-informatique'].decode('utf8')]
        form.find_button_by_label('Sauvegarder').click()

    def step_3d(self, browser):
        """The actor fills in element with a deadline date greater than one of the parents."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_dublinCore_form_widget_name] = u"Titre"
        fields[self.planned_end_date_day_form_widget_name] = u"1"
        fields[self.planned_end_date_month_form_widget_name] = u"1"
        fields[self.planned_end_date_year_form_widget_name] = u"2021"
        fields[self.manager_form_widget_name] = [self.services_config['service-informatique'].decode('utf8')]
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser):
        """The system creates and displays the element with "Saved changes" info success."""
        statusmessages.assert_message(u'Elément créé')
        # catalog check
        context = browser.context
        brain = api.content.find(context=context, depth=0)[0]
        self.assertIn(context.title, brain.Title)
        self.assertEqual(context.categories, brain.categories)
        self.assertEqual(context.manager, brain.manager)
        self.assertEqual(context.planned_begin_date, brain.planned_begin_date)
        self.assertEqual(context.effective_begin_date, brain.effective_begin_date)
        self.assertEqual(context.planned_end_date, brain.planned_end_date)
        self.assertEqual(context.effective_end_date, brain.effective_end_date)
        self.assertEqual(context.progress, brain.progress)
        self.assertEqual(context.sdgs, brain.sdgs)

    def step_4a(self, browser, context):
        """The system back to the previous page with "Addition canceled" Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u"Ajout annulé")

    def step_4b(self, browser):
        """The system creates the pst action with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (A.25)', heading.text)
        statusmessages.assert_message(u"Elément créé")

    def step_4c(self, browser):
        """The system displays warnings, (Back to the step 2)."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Action', heading.text)
        self.assertTrue('Champ obligatoire' in browser.contents)
        statusmessages.assert_message(u"Il y a des erreurs.")

    def step_4d(self, browser):
        """The system creates the pst action with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (A.26)', heading.text)
        statusmessages.assert_message(u"Elément créé")

