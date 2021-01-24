# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor adds pst sub action."""
    browser.open(context.absolute_url() + '/++add++pstsubaction')


def step_3a(browser):
    """The actor cancels the form."""
    form = browser.forms['form']
    form.find_button_by_label('Annuler').click()


def step_3b(browser):
    """The actor fills in the fields but omit mandatory fields and save."""
    form = browser.forms['form']
    form.find_button_by_label('Sauvegarder').click()


class TestCreatePstSubAction(FunctionalTestCase):
    """Use case tests.
    Name: Create a pst sub action
    Actor(s): pst admin, pst editors, manager
    Goal: allows actors to create a pst sub action
    Author: Franck Ngaha
    Created: 18/01/2021
    Updated: 19/01/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst editor in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a manager in the context of a pst action in anyone of following states (created, ongoing, to_be_scheduled)
    """

    def setUp(self):
        super(TestCreatePstSubAction, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.manager = {'username': 'agent', 'password': self.password}
        # Contexts
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_10 = self.pst['etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-'
                              'de-serre-afin-dassurer-le-developpement-durable']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']
        self.a_16 = self.oo_15['reduire-la-consommation-energetique-de-ladministration-communale']
        # scenarios
        self.scenarios = ['main_scenario', 'alternative_scenario_3a', 'exceptional_scenario_3b']

    @browsing
    def test_scenarios_as_admin_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a_16, transition='back_to_created')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a_16)

    @browsing
    def test_scenarios_as_admin_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_admin, self.a_16)

    @browsing
    def test_scenarios_as_admin_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a_16, transition='begin')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.a_16)

    @browsing
    def test_scenarios_as_admin_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a_16, transition='stop')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_admin, self.a_16)

    @browsing
    def test_scenarios_as_admin_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a_16, transition='begin')
        api.content.transition(obj=self.a_16, transition='finish')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_admin, self.a_16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a_16, transition='back_to_created')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a_16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_editor, self.a_16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a_16, transition='begin')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.a_16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a_16, transition='stop')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_editor, self.a_16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a_16, transition='begin')
        api.content.transition(obj=self.a_16, transition='finish')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_editor, self.a_16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a_16, transition='back_to_created')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.a_16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.manager, self.a_16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a_16, transition='begin')
        state = api.content.get_state(obj=self.a_16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.a_16)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor adds pst sub action
        self.step_2(browser, context)  # The system calculates default values and displays the form
        self.step_3(browser)  # The actor fills in fields and save
        self.step_4(browser)  # The system creates and displays the pst sub action

    def alternative_scenario_3a(self, browser, actor, context):
        """The actor cancels the form."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser, context)
        step_3a(browser)  # The actor cancels the form
        self.step_4a(browser, context)  # The system back to the previous page with "Addition canceled" Info

    def exceptional_scenario_3b(self, browser, actor, context):
        """The actor fills in the fields but omit a mandatory field and save."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser, context)
        step_3b(browser)  # The actor fills in the fields but omit mandatory fields
        self.step_4b(browser)  # system warn, (back to the step 2)

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser, context):
        """
        The system calculates the default values of the 'Categories' and 'Plans' fields,
        pre-populates and displays add sub action form
        """
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Sous-action', heading.text)
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

    def step_4(self, browser):
        """The system creates and displays the element with "Saved changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (SA.24)', heading.text)
        statusmessages.assert_message(u'Elément créé')

    def step_4a(self, browser, context):
        """The system back to the previous page with "Addition canceled" Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u"Ajout annulé")

    def step_4b(self, browser):
        """The system displays warnings, (Back to the step 2)."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Sous-action', heading.text)
        self.assertTrue('Champ obligatoire' in browser.contents)
        statusmessages.assert_message(u"Il y a des erreurs.")
