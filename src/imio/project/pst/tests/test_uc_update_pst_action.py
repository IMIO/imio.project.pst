# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.core.utils import get_global_budget_infos
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor opens edit form."""
    browser.open(context.absolute_url() + '/edit')


def step_3a(browser):
    """The actor cancels the form."""
    form = browser.forms['form']
    form.find_button_by_label('Annuler').click()


class TestUpdatePstAction(FunctionalTestCase):
    """Use case tests.
    Name: Update a pst action
    Actor(s): pst admin, pst editors, manager
    Goal: allows actors to update a pst action
    Author: Franck Ngaha
    Created: 26/01/2021
    Updated: 26/01/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst action in anyone of all his states
    (created, to_be_schedule, ongoing, stopped, terminated)
    - a pst editor in the context of a pst action in anyone of all his states
    (created, to_be_schedule, ongoing, stopped, terminated)
    - a manager in the context of a pst action in anyone of all his states
    (created, to_be_scheduled, ongoing, stopped, terminated)
    """

    def setUp(self):
        super(TestUpdatePstAction, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.manager = {'username': 'agent', 'password': self.password}
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'alternative_scenario_3b',
            'alternative_scenario_3c',
            'alternative_scenario_3d',
        ]

    @browsing
    def test_scenarios_as_admin_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a16, transition='back_to_created')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_admin_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_admin_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_admin_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a16, transition='stop')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_admin_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        api.content.transition(obj=self.a16, transition='finish')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a16, transition='back_to_created')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_editor, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a16, transition='stop')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_editor, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        api.content.transition(obj=self.a16, transition='finish')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_editor, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a16, transition='back_to_created')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.manager, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.a16)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor opens edit form
        self.step_2(browser)  # The system displays pst action's edit form
        self.step_3(browser)  # The actor update fields and save
        self.step_4(browser, context)  # The system updates summarized fields and save changes with "Modify changes"
        # info success

    def alternative_scenario_3a(self, browser, actor, context):
        """The actor cancel the form."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        step_3a(browser)  # The actor cancels the form
        self.step_4a(browser, context)  # The system back to the previous page with "Modification canceled" Info

    def alternative_scenario_3b(self, browser, actor, context):
        """The actor remove the deadline and save."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        self.step_3b(browser)  # The actor removes the deadline
        self.step_4b(browser)  # The system displays the max deadline of the contained items with warning message

    def alternative_scenario_3c(self, browser, actor, context):
        """
        The actor fills a deadline smaller than the largest of their children.
        (30/09/2020) < (sa_18, 31/10/2020)
        """
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        self.step_3c(browser)  # The actor fills a smaller deadline
        self.step_4c(browser, context)  # The system updates element with warning message

    def alternative_scenario_3d(self, browser, actor, context):
        """
        The actor fills a deadline greater than one of their parents.
        (01/01/2025) < (oo15, 31/12/2024)
        """
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        self.step_3d(browser)  # The actor fills a greater deadline
        self.step_4d(browser, context)  # The system updates element with warning message

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays pst action's edit form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Editer Action', heading.text)

    def step_3(self, browser):
        """The actor update fields and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_dublinCore_form_widget_name] = u'Titre'
        browser.find('Financement/Budget').fill(
            [{u'Montant': '500,0', u'Type de budget': 'wallonie', u'Ann\xe9e': '2021'}])
        form.find_button_by_label('Sauvegarder').click()

    def step_3b(self, browser):
        """The actor remove the deadline and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.planned_end_date_day_form_widget_name] = u''
        fields[self.planned_end_date_month_form_widget_name] = u''
        fields[self.planned_end_date_year_form_widget_name] = u''
        form.find_button_by_label('Sauvegarder').click()

    def step_3c(self, browser):
        """The actor fills a smaller deadline."""
        form = browser.forms['form']
        fields = form.values
        fields[self.planned_end_date_day_form_widget_name] = u'30'
        fields[self.planned_end_date_month_form_widget_name] = u'9'
        fields[self.planned_end_date_year_form_widget_name] = u'2020'
        form.find_button_by_label('Sauvegarder').click()

    def step_3d(self, browser):
        """The actor fills a greater deadline."""
        form = browser.forms['form']
        fields = form.values
        fields[self.planned_end_date_day_form_widget_name] = u'1'
        fields[self.planned_end_date_month_form_widget_name] = u'1'
        fields[self.planned_end_date_year_form_widget_name] = u'2025'
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser, context):
        """The system updates summarized fields and save changes with "Modify changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (A.16)', heading.text)
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(get_global_budget_infos(context.aq_parent),
                         {'europe': 500.0, 'wallonie': 7000.0, 'autres': 500.0, 'federal': 500.0})
        self.assertEqual(get_global_budget_infos(context.aq_parent.aq_parent),
                         {'europe': 5800.0, 'wallonie': 7550.0, 'ville': 5430.0, 'federal': 500.0, 'autres': 500.0,
                          'federation-wallonie-bruxelles': 520.55})

    def step_4a(self, browser, context):
        """The system back to the previous page with 'Modification canceled' Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u'Modification annulée')

    def step_4b(self, browser):
        """The system displays the max deadline of the contained items with a warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u"Titre (A.16)", heading.text)
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance n'est pas renseignée sur cet élément, le système affiche la plus "
             u"grande de ses éventuels enfants."]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['31/10/2020'])

    def step_4c(self, browser, context):
        """The system updates element with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title(), heading.text)
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance d'un des enfants est supérieure à celles de cet élément."]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['30/09/2020'])

    def step_4d(self, browser, context):
        """The system updates element with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title(), heading.text)
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance de cet élément est supérieure à au moins une de ses parents."]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['01/01/2025'])
