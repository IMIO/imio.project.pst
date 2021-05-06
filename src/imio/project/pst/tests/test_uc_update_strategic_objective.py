# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
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


class TestUpdateStrategicObjective(FunctionalTestCase):
    """Use case tests.
    Name: Update a strategic objective
    Actor(s): pst admin, pst editors, administrative responsible
    Goal: allows actors to update a strategic objective
    Author: Franck Ngaha
    Created: 06/05/2021
    Updated: 06/05/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of an strategic objective in anyone of all his states (created, ongoing, achieved)
    - a pst editor in the context of an strategic objective in anyone of all his states (created, ongoing, achieved)
    """

    def setUp(self):
        super(TestUpdateStrategicObjective, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
        ]

    @browsing
    def test_scenarios_as_admin_in_strategic_objective_created(self, browser):
        api.content.transition(obj=self.os1, transition='back_to_created')
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.os1)

    @browsing
    def test_scenarios_as_admin_in_strategic_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.os1)

    @browsing
    def test_main_scenario_as_admin_in_strategic_objective_achieved(self, browser):
        api.content.transition(obj=self.os1, transition='achieve')
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_admin, self.os1)

    @browsing
    def test_scenarios_as_pst_editor_in_strategic_objective_created(self, browser):
        api.content.transition(obj=self.os1, transition='back_to_created')
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_editor, self.os1)

    @browsing
    def test_scenarios_as_pst_editor_in_strategic_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.os1)

    @browsing
    def test_main_scenario_as_pst_editor_in_strategic_objective_achieved(self, browser):
        api.content.transition(obj=self.os1, transition='achieve')
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_editor, self.os1)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor opens edit form
        self.step_2(browser)  # The system displays strategic objective's edit form
        self.step_3(browser)  # The actor update fields and save
        self.step_4(browser)  # The system save changes with "Modify changes" info success

    def alternative_scenario_3a(self, browser, actor, context):
        """The actor cancel the form."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        step_3a(browser)  # The actor cancels the form
        self.step_4a(browser, context)  # The system back to the previous page with "Modification canceled" Info

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays strategic objective's edit form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Editer Objectif stratégique', heading.text)

    def step_3(self, browser):
        """The actor update fields and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_dublinCore_form_widget_name] = u'Titre'
        browser.find('Financement/Budget').fill(
            [{u'Montant': '500,0', u'Type de budget': 'wallonie', u'Ann\xe9e': '2021'}])
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser):
        """The system save changes with "Modify changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (OS.1)', heading.text)
        statusmessages.assert_message(u'Modifications sauvegardées')

    def step_4a(self, browser, context):
        """The system back to the previous page with 'Modification canceled' Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u'Modification annulée')
