# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor adds task."""
    browser.open(context.absolute_url() + '/++add++task')


def step_3a(browser):
    """The actor cancels the form."""
    form = browser.forms['form']
    form.find_button_by_label('Annuler').click()


def step_3b(browser):
    """The actor fills in the fields but omit mandatory fields and save."""
    form = browser.forms['form']
    form.find_button_by_label('Sauvegarder').click()


class TestCreateTask(FunctionalTestCase):
    """Use case tests.
    Name: Create a task
    Actor(s): pst admin, pst editors, manager
    Goal: allows actors to create a task
    Author: Franck Ngaha
    Created: 21/01/2021
    Updated: 24/01/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst action (which does not contain any sub-actions) in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst admin in the context of a pst sub action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst editor in the context of a pst action (which does not contain any sub-actions) in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst editor in the context of a pst sub action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a manager in the context of a pst action (which does not contain any sub-actions) in anyone of following states
    (created, ongoing, to_be_scheduled)
    - a manager in the context of a pst sub action in anyone of following states (created, ongoing, to_be_scheduled)
    """

    def setUp(self):
        super(TestCreateTask, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.manager = {'username': 'agent', 'password': self.password}
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'alternative_scenario_3c',
            'exceptional_scenario_3b',
            'alternative_scenario_3d',
        ]

    @browsing
    def test_scenarios_as_admin_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a3, transition='back_to_created')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a3)

    @browsing
    def test_scenarios_as_admin_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_admin, self.a3)

    @browsing
    def test_scenarios_as_admin_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a3, transition='begin')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.a3)

    @browsing
    def test_scenarios_as_admin_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a3, transition='stop')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_admin, self.a3)

    @browsing
    def test_scenarios_as_admin_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a3, transition='begin')
        api.content.transition(obj=self.a3, transition='finish')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_admin, self.a3)

    @browsing
    def test_scenarios_as_admin_in_pst_sub_action_created(self, browser):
        api.content.transition(obj=self.a16, transition='back_to_created')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_admin_in_pst_sub_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_admin_in_pst_sub_action_ongoing(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_admin_in_pst_sub_action_stopped(self, browser):
        api.content.transition(obj=self.a16, transition='stop')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_admin_in_pst_sub_action_terminated(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        api.content.transition(obj=self.a16, transition='finish')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a3, transition='back_to_created')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_editor, self.a3)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_editor, self.a3)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a3, transition='begin')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.a3)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a3, transition='stop')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_editor, self.a3)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a3, transition='begin')
        api.content.transition(obj=self.a3, transition='finish')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_editor, self.a3)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_sub_action_created(self, browser):
        api.content.transition(obj=self.a16, transition='back_to_created')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_editor, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_sub_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_editor, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_sub_action_ongoing(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_sub_action_stopped(self, browser):
        api.content.transition(obj=self.a16, transition='stop')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_editor, self.a16)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_sub_action_terminated(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        api.content.transition(obj=self.a16, transition='finish')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_editor, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a3, transition='back_to_created')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.a3)

    @browsing
    def test_scenarios_as_manager_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.manager, self.a3)

    @browsing
    def test_scenarios_as_manager_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a3, transition='begin')
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.a3)

    @browsing
    def test_scenarios_as_manager_in_pst_sub_action_created(self, browser):
        api.content.transition(obj=self.a16, transition='back_to_created')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_sub_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.manager, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_sub_action_ongoing(self, browser):
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
        step_1(browser, context)  # The actor adds task
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

    def alternative_scenario_3c(self, browser, actor, context):
        """The actor fills in the fields but not the deadline and save."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser, context)
        self.step_3c(browser)  # The actor fills in the fields but not the deadline
        self.step_4c(browser)  # The system creates the task with warning message

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
        The system calculates the default value of the 'assigned_group' field,
        pre-populates and displays add task form
        """
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Tâche', heading.text)
        form = browser.forms['form']
        fields = form.values
        assigned_group = fields[self.assigned_group_form_widget_name]
        self.assertTrue(assigned_group.__eq__(set(getattr(context, 'assigned_group', []))))

    def step_3(self, browser):
        """The actor fills in the form and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_form_widget_name] = u"Titre"
        fields[self.description_task_form_widget_name] = u"Description de la tâche"
        fields[self.assigned_user_form_widget_name] = 'agent'
        fields[self.due_date_day_form_widget_name] = u"31"
        fields[self.due_date_month_form_widget_name] = u"3"
        fields[self.due_date_year_form_widget_name] = u"2020"
        form.find_button_by_label('Sauvegarder').click()

    def step_3c(self, browser):
        """The actor fills in the fields but not the deadline and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_form_widget_name] = u"Titre"
        form.find_button_by_label('Sauvegarder').click()

    def step_3d(self, browser):
        """The actor fills in element with a deadline date greater than one of the parents."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_form_widget_name] = u"Titre"
        fields[self.due_date_day_form_widget_name] = u"31"
        fields[self.due_date_month_form_widget_name] = u"7"
        fields[self.due_date_year_form_widget_name] = u"2020"
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser):
        """The system creates and displays the element with "Saved changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre', heading.text)
        statusmessages.assert_message(u'Elément créé')

    def step_4a(self, browser, context):
        """The system back to the previous page with "Addition canceled" Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u"Ajout annulé")

    def step_4b(self, browser):
        """The system displays warnings, (Back to the step 2)."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Tâche', heading.text)
        self.assertTrue('Champ obligatoire' in browser.contents)
        statusmessages.assert_message(u"Il y a des erreurs.")

    def step_4c(self, browser):
        """The system creates the task with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre', heading.text)
        statusmessages.assert_message(u"Elément créé")

    def step_4d(self, browser):
        """The system creates the pst action with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre', heading.text)
        statusmessages.assert_message(u"Elément créé")
