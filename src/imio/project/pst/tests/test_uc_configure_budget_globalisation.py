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


def step_3(browser):
    """The actor update globalisation budget fields and save."""
    form = browser.forms['form']

    # remove u'À programmer' to pstaction_budget_states
    browser.find(u'États à considérer pour la globalisation des champs financiers du type Action').fill(
        [u'En cours', u'Finalisé', ])

    # fill some fields to avoid widget errors
    browser.find(u'Catégories possibles').fill([
        {u'Libellé': u"Volet interne : Administration générale - Amélioration de l'Administration",
         u'Clé': 'volet-interne-adm-generale-amelioration-administration'}])
    browser.find(u'Priorités possibles').fill([{u'Libellé': '1', u'Clé': '1'}])
    browser.find(u'Types de budget possibles').fill([{u'Libellé': 'Wallonie', u'Clé': 'wallonie'}])
    browser.find(u'Plans possibles').fill([{u'Libellé': 'Plan de gestion', u'Clé': 'plan-de-gestion'}])
    browser.find(u'Colonnes à afficher sur les objectifs stratégiques').fill(
        [u'Sélection', u'Titre (lien)', u'État', u'Catégories', u'Modifié le', u'Actions PST'])
    browser.find(u'Colonnes à afficher sur les objectifs opérationnels').fill(
        [u'Sélection', u'Titre (lien)', u'Parents', u'État', u'Gestionnaire', u'Échéance', u'Priorité',
         u'Catégories', u'O.D.D.', u'Modifié le', u'Actions PST'])
    browser.find(u'Colonnes à afficher sur les actions').fill(
        [u'Sélection', u'Titre (lien)', u'Parents', u'État', u'Gestionnaire', u'Porteur', u'Date début prévue',
         u'Échéance', u'Date début effective', u'Date fin effective', u'Progression', u'Indice de santé',
         u'O.D.D.', u'Modifié le', u'Actions PST'])
    browser.find(u'Colonnes à afficher sur les tâches').fill(
        [u'Sélection', u'Titre (lien)', u'Parents', u'État', u'Groupe assigné', u'Utilisateur assigné',
         u'Échéance', u'Créé le', u'Modifié le', u'Actions PST'])
    browser.find(u'États à considérer pour la globalisation des champs financiers du type Objectif stratégique').fill(
        [u'En cours', u'Clôturé'])
    browser.find(u'États à considérer pour la globalisation des champs financiers du type Objectif opérationnel').fill(
        [u'En cours', u'Clôturé'])

    form.find_button_by_label('Sauvegarder').click()


class TestConfigureBudgetGlobalizationOfActionsSub(FunctionalTestCase):
    """Use case tests.
    Name: Configure budget globalisation of (sub) actions
    Actor(s): pst admin
    Goal: allow actor to configure states to be considered for the budget globalisation
    Author: Franck Ngaha
    Created: 16/04/2021
    Updated: 20/04/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst project space in state (internally_published)
    """

    def setUp(self):
        super(TestConfigureBudgetGlobalizationOfActionsSub, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        # Contexts
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        # scenarios
        self.scenarios = [
            'main_scenario',
        ]

    @browsing
    def test_scenarios_as_admin_in_pst_project_space_internally_published(self, browser):
        state = api.content.get_state(obj=self.pst)
        self.assertEqual(state, 'internally_published')
        self.call_scenarios(browser, self.pst_admin, self.pst)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor opens edit form
        self.step_2(browser)  # The system displays pst project space edit form
        step_3(browser)  # The actor update pstaction_budget_states fields and save
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

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays pst project space edit form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Editer Espace de projets PST', heading.text)

    def step_4(self, browser, context):
        """The system updates summarized fields and save changes with "Modify changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u'Modifications sauvegardées')
        os_10 = context[
            'etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-de-serre-afin-dassu'
            'rer-le-developpement-durable']
        self.assertEqual(get_global_budget_infos(os_10), {})

    def step_4a(self, browser, context):
        """The system back to the previous page with 'Modification canceled' Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u'Modification annulée')
