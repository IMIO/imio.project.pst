# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor adds sub action link."""
    browser.open(context.absolute_url() + '/++add++subaction_link')


class TestCreateSubActionLink(FunctionalTestCase):
    """Use case tests.
    Name: Create a sub action link
    Actor(s): pst admin, pst editors, manager
    Goal: allows actors to create a sub action link
    Author: Franck Ngaha
    Created: 30/01/2021
    Updated: 30/01/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst editor in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a manager in the context of a pst action in anyone of following states (created, ongoing, to_be_scheduled)
    """

    def setUp(self):
        super(TestCreateSubActionLink, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.manager = {'username': 'agent', 'password': self.password}
        # Contexts
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_10 = self.pst['etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-'
                              'de-serre-afin-dassurer-le-developpement-durable']
        self.oo_11 = self.os_10[
            'doter-la-commune-de-competences-en-matiere-energetique-pour-fin-2021-compte-tenu-du-budget']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']
        self.a_13 = self.oo_11['repondre-a-lappel-a-projet-ecopasseur-de-la-wallonie']
        self.a_16 = self.oo_15['reduire-la-consommation-energetique-de-ladministration-communale']
        self.sa_17 = self.a_16['realiser-un-audit-energetique-du-batiment']
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'exceptional_scenario_3b',
        ]

    @browsing
    def test_scenarios_as_admin_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a_13, transition='back_to_created')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a_13)

    @browsing
    def test_scenarios_as_admin_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_admin, self.a_13)

    @browsing
    def test_scenarios_as_admin_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a_13, transition='begin')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.a_13)

    @browsing
    def test_scenarios_as_admin_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a_13, transition='stop')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_admin, self.a_13)

    @browsing
    def test_scenarios_as_admin_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a_13, transition='begin')
        api.content.transition(obj=self.a_13, transition='finish')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_admin, self.a_13)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a_13, transition='back_to_created')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a_13)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_editor, self.a_13)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a_13, transition='begin')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.a_13)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a_13, transition='stop')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_editor, self.a_13)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a_13, transition='begin')
        api.content.transition(obj=self.a_13, transition='finish')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_editor, self.a_13)

    @browsing
    def test_scenarios_as_manager_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a_13, transition='back_to_created')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.a_13)

    @browsing
    def test_scenarios_as_manager_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.manager, self.a_13)

    @browsing
    def test_scenarios_as_manager_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a_13, transition='begin')
        state = api.content.get_state(obj=self.a_13)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.a_13)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor adds sub action link
        self.step_2(browser)  # The system displays the form
        self.step_3(browser)  # The actor fills in fields and save
        self.step_4(browser)  # The system creates, cheks unicity and displays the sub action link with warning message

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
        """The system displays add sub action link form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Lien sous-action', heading.text)

    def step_3(self, browser):
        """The actor fills in the form and save."""
        browser.find('Lien symbolique').fill(self.sa_17)
        browser.find('Sauvegarder').click()

    def step_3a(self, browser):
        """The actor cancels the form."""
        browser.find(self.cancel_button_name).click()

    def step_3b(self, browser):
        """The actor fills in the fields but omit mandatory fields and save."""
        browser.find(self.save_button_name).click()

    def step_4(self, browser):
        """
        The system creates, check unicity and displays the element with "Saved changes" info success and mirror
        link warning.
        """
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u"Réaliser un audit énergétique du bâtiment (SA.17)", heading.text)
        statusmessages.assert_message(u'Elément créé')
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            ["Avertissement Ce contenu est une copie miroir ! Cliquer sur ce lien Modifier pour modifier l'original"]
        )
        sal_17 = self.a_13['realiser-un-audit-energetique-du-batiment']
        self.assertNotEqual(self.sa_17.UID(), sal_17.UID())

    def step_4a(self, browser, context):
        """The system back to the previous page with "Addition canceled" Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u"Ajout annulé")

    def step_4b(self, browser):
        """The system displays warnings, (Back to the step 2)."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Lien sous-action', heading.text)
        self.assertTrue('Champ obligatoire' in browser.contents)
        statusmessages.assert_message(u"Il y a des erreurs.")
