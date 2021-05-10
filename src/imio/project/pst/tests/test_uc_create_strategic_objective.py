# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor adds strategic objective."""
    browser.open(context.absolute_url() + '/++add++strategicobjective')


def step_3a(browser):
    """The actor cancel the form."""
    form = browser.forms['form']
    form.find_button_by_label('Annuler').click()


def step_3b(browser):
    """The actor fills in the fields but not the deadline and save."""
    browser.find_button_by_label('Sauvegarder').click()


class TestCreateStrategicObjective(FunctionalTestCase):
    """Use case tests.
    Name: Create a strategic objective
    Actor(s): pst admin, pst editors
    Goal: allows actors to create a strategic objective
    Author: Franck Ngaha
    Created: 06/05/2020
    Updated: 06/05/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst project space in state (internally_published)
    - a pst editor in the context of a pst project space in state (internally_published)
    """

    def setUp(self):
        super(TestCreateStrategicObjective, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'exceptional_scenario_3b'
        ]

    @browsing
    def test_scenarios_as_admin_in_pst_project_space_internally_published(self, browser):
        state = api.content.get_state(obj=self.pst)
        self.assertEqual(state, 'internally_published')
        self.call_scenarios(browser, self.pst_admin, self.pst)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_project_space_internally_published(self, browser):
        state = api.content.get_state(obj=self.pst)
        self.assertEqual(state, 'internally_published')
        self.call_scenarios(browser, self.pst_editor, self.pst)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor adds strategic objective
        self.step_2(browser)  # The system displays the form
        self.step_3(browser)  # The actor fills in fields and save
        self.step_4(browser)  # The system creates and displays the strategic objective

    def alternative_scenario_3a(self, browser, actor, context):
        """The actor cancels the form."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        step_3a(browser)  # The actor cancels the form
        self.step_4a(browser, context)  # The system back to the previous page with "Addition canceled" Info

    def exceptional_scenario_3b(self, browser, actor, context):
        """The actor fills in the fields but omit a mandatory field and save."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        step_3b(browser)  # The actor fills in the fields but omit mandatory fields
        self.step_4b(browser)  # system warn, (back to the step 2)

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays add action form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Objectif stratégique', heading.text)

    def step_3(self, browser):
        """The actor fills in the form and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_dublinCore_form_widget_name] = u"Titre"
        fields[self.description_rich_form_widget_name] = u"Description"
        fields[self.categories_form_widget_name] = ["volet-interne-adm-generale-accessibilite-administration"]
        fields[self.plan_form_widget_name] = ["plan-de-gestion"]
        fields[self.budget_type_form_widget_name] = u"wallonie"
        fields[self.budget_year_form_widget_name] = u"2021"
        fields[self.budget_amount_form_widget_name] = u"10000,0"
        fields[self.budget_comments_form_widget_name] = u"Commentaires sur le financement/budget"
        fields[self.observation_form_widget_name] = u"Constat"
        fields[self.comments_form_widget_name] = u"Commentaires"
        form.find_button_by_label('Sauvegarder').click()
        # write browser contents
        # with open('browser_contents', 'w') as f:
        #     f.write(browser.contents)

    def step_4(self, browser):
        """The system creates and displays the element with "Saved changes" info success."""
        statusmessages.assert_message(u'Elément créé')
        # catalog check
        context = browser.context
        brain = api.content.find(context=context, depth=0)[0]
        self.assertIn(context.title, brain.Title)
        self.assertEqual(context.categories, brain.categories)

    def step_4a(self, browser, context):
        """The system back to the previous page with "Addition canceled" Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u"Ajout annulé")

    def step_4b(self, browser):
        """The system displays warnings, (Back to the step 2)."""
        # write browser contents
        # with open('browser_contents', 'w') as f:
        #     f.write(browser.contents)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Objectif stratégique', heading.text)
        self.assertTrue('Champ obligatoire' in browser.contents)
        statusmessages.assert_message(u"Il y a des erreurs.")
