# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor adds action link."""
    browser.open(context.absolute_url() + '/++add++action_link')


class TestCreateActionLink(FunctionalTestCase):
    """Use case tests.
    Name: Create an action link
    Actor(s): pst admin, pst editors, administrative responsible, manager
    Goal: allows actors to create an action link
    Author: Franck Ngaha
    Created: 29/01/2021
    Updated: 31/01/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - a pst editor in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - an administrative responsible in the context of an operational objective in state ongoing
    - a manager in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    """

    def setUp(self):
        super(TestCreateActionLink, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.adm_resp = {'username': 'chef', 'password': self.password}
        self.manager = {'username': 'agent', 'password': self.password}
        # Contexts
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_1 = self.pst['etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient']
        self.oo_2 = self.os_1[
            'diminuer-le-temps-dattente-de-lusager-au-guichet-population-de-20-dans-les-12-mois-a-venir']
        self.oo_6 = self.os_1['optimiser-laccueil-au-sein-de-ladministration-communale']
        self.a_7 = self.oo_6['placer-des-pictogrammes-de-guidance']
        self.t1 = self.a_7['acheter-fournir-des-pictogrammes-de-guidance']
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'exceptional_scenario_3b',
        ]

    @browsing
    def test_scenarios_as_admin_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo_2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.oo_2)

    @browsing
    def test_scenarios_as_admin_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.oo_2)

    @browsing
    def test_main_scenario_as_admin_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo_2, transition='achieve')
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_admin, self.oo_2)

    @browsing
    def test_scenarios_as_pst_editor_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo_2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_editor, self.oo_2)

    @browsing
    def test_scenarios_as_pst_editor_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.oo_2)

    @browsing
    def test_main_scenario_as_pst_editor_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo_2, transition='achieve')
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_editor, self.oo_2)

    @browsing
    def test_scenarios_as_adm_resp_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.adm_resp, self.oo_2)

    @browsing
    def test_scenarios_as_manager_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo_2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.oo_2)

    @browsing
    def test_scenarios_as_manager_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.oo_2)

    @browsing
    def test_main_scenario_as_manager_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo_2, transition='achieve')
        state = api.content.get_state(obj=self.oo_2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.manager, self.oo_2)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor adds action link
        self.step_2(browser)  # The system displays the form
        self.step_3(browser)  # The actor fills in field and save
        self.step_4(browser)  # The system creates, check unicity and displays the action link with warning message

    def alternative_scenario_3a(self, browser, actor, context):
        """The actor cancels the form."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        self.step_3a(browser)  # The actor cancels the form
        self.step_4a(browser, context)  # The system back to the previous page with "Addition canceled" Info

    def exceptional_scenario_3b(self, browser, actor, context):
        """The actor fills in the fields but omit a mandatory field and save."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        self.step_3b(browser)  # The actor fills in the fields but omit mandatory fields
        self.step_4b(browser)  # system warn, (back to the step 2)

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays add action link form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Lien action', heading.text)

    def step_3(self, browser):
        """The actor fills in the form and save."""
        browser.find('Lien symbolique').fill(self.a_7)
        browser.find('Sauvegarder').click()

    def step_3a(self, browser):
        """The actor cancels the form."""
        browser.find(self.cancel_button_name).click()

    def step_3b(self, browser):
        """The actor fills in the fields but omit mandatory fields and save."""
        browser.find(self.save_button_name).click()

    def step_4(self, browser):
        """
        The system creates, check unicity and displays the element with "Saved changes" info success and original
        link warning.
        """
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Placer des pictogrammes de guidance (A.7)', heading.text)
        statusmessages.assert_message(u'Elément créé')
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            ["Avertissement Ce contenu est une copie miroir ! Cliquer sur ce lien Modifier pour modifier l'original"]
        )
        al_7 = self.oo_2['placer-des-pictogrammes-de-guidance']
        tl1 = al_7['acheter-fournir-des-pictogrammes-de-guidance']
        a_7_brain = api.content.find(context=self.a_7, depth=0)[0]
        al_7_brain = api.content.find(context=al_7, depth=0)[0]
        self.assertNotEqual(a_7_brain.UID, al_7_brain.UID)
        t1_brain = api.content.find(context=self.t1, depht=0)[0]
        tl1_brain = api.content.find(context=tl1, depth=0)[0]
        self.assertNotEqual(t1_brain.UID, tl1_brain.UID)

    def step_4a(self, browser, context):
        """The system back to the previous page with "Addition canceled" Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u"Ajout annulé")

    def step_4b(self, browser):
        """The system displays warnings, (Back to the step 2)."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Lien action', heading.text)
        self.assertTrue('Champ obligatoire' in browser.contents)
        statusmessages.assert_message(u"Il y a des erreurs.")
