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


class TestUpdateOperationalObjective(FunctionalTestCase):
    """Use case tests.
    Name: Update an operational objective
    Actor(s): pst admin, pst editors, administrative responsible
    Goal: allows actors to update an operational objective
    Author: Franck Ngaha
    Created: 25/11/2020
    Updated: 25/01/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - a pst editor in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - an administrative responsible in the context of an operational objective state (ongoing)
    """

    def setUp(self):
        super(TestUpdateOperationalObjective, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.adm_resp = {'username': 'chef', 'password': self.password}
        # Contexts
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_10 = self.pst[
            'etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-de-serre-afin-dassu'
            'rer-le-developpement-durable']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'alternative_scenario_3b',
            'alternative_scenario_3c',
        ]

    @browsing
    def test_scenarios_as_admin_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo_15, transition='back_to_created')
        state = api.content.get_state(obj=self.oo_15)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.oo_15)

    @browsing
    def test_scenarios_as_admin_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo_15)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.oo_15)

    @browsing
    def test_main_scenario_as_admin_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo_15, transition='achieve')
        state = api.content.get_state(obj=self.oo_15)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_admin, self.oo_15)

    @browsing
    def test_scenarios_as_pst_editor_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo_15, transition='back_to_created')
        state = api.content.get_state(obj=self.oo_15)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_editor, self.oo_15)

    @browsing
    def test_scenarios_as_pst_editor_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo_15)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.oo_15)

    @browsing
    def test_main_scenario_as_pst_editor_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo_15, transition='achieve')
        state = api.content.get_state(obj=self.oo_15)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_editor, self.oo_15)

    @browsing
    def test_scenarios_as_adm_resp_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo_15)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.adm_resp, self.oo_15)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor opens edit form
        self.step_2(browser)  # The system displays operational objective's edit form
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
        (2023, 06, 30) < (2024, 06, 30)
        """
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        self.step_3c(browser)  # The actor fills a smaller planned end date
        self.step_4c(browser, context)  # The system updates element with warning message

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays operational objective's edit form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Editer Objectif opérationnel', heading.text)

    def step_3(self, browser):
        """The actor update fields and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_dublinCore_form_widget_name] = u'Titre'
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
        """The actor fills a smaller planned end date."""
        form = browser.forms['form']
        fields = form.values
        fields[self.planned_end_date_day_form_widget_name] = u'30'
        fields[self.planned_end_date_month_form_widget_name] = u'6'
        fields[self.planned_end_date_year_form_widget_name] = u'2023'
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser):
        """The system save changes with "Modify changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (OO.15)', heading.text)
        statusmessages.assert_message(u'Modifications sauvegardées')

    def step_4a(self, browser, context):
        """The system back to the previous page with 'Modification canceled' Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u'Modification annulée')

    def step_4b(self, browser):
        """The system displays the max deadline of the contained items with a warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u"Titre (OO.15)", heading.text)
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance n'est pas renseignée sur cet élément, le système affiche la plus "
             u"grande de ses éventuels enfants."]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['30/06/2024'])

    def step_4c(self, browser, context):
        """The system updates element with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title(), heading.text)
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance d'un des enfants est supérieure à celles de cet élément."]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['30/06/2023'])
