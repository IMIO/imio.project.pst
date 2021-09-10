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
    """The actor clicks on "Split budget lines between multiple instances"."""
    browser.open('{}/@@budget_split'.format(context.absolute_url()))


class TestBudgetSplit(FunctionalTestCase):
    """Use case tests.
    Name: Split of budgets between the different actions
    Actor(s): pst admin, pst editors, manager
    Goal: allows actors to split of budgets between the different actions
    Author: Franck Ngaha
    Created: 10/09/2021
    Updated: 10/09/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst action in anyone of all his states
    (created, to_be_schedule, ongoing, stopped, terminated)
    - a pst admin in the context of a pst sub action in anyone of all his states
    (created, to_be_schedule, dongoing, stopped, terminated)
    - a pst editor in the context of a pst action in anyone of all his states
    (created, to_be_schedule, ongoing, stopped, terminated)
    - a pst editor in the context of a pst sub action in anyone of all his states
    (created, to_be_schedule, dongoing, stopped, terminated)
    - a manager in the context of a pst action in anyone of all his states
    (created, to_be_scheduled, ongoing, stopped, terminated)
    - a manager in the context of a pst sub action in anyone of all his states
    (created, to_be_scheduled, ongoing, stopped, terminated)
    """

    def setUp(self):
        super(TestBudgetSplit, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.manager = {'username': 'agent', 'password': self.password}
        # scenarios
        self.scenarios = [
            'main_scenario',
        ]

    # admin ------------------------------------------------------------------------------------------------------------
    @browsing
    def test_scenarios_as_admin_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a4, transition='back_to_created')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a4)

    @browsing
    def test_scenarios_as_admin_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_admin, self.a4)

    @browsing
    def test_scenarios_as_admin_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a4, transition='begin')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.a4)

    @browsing
    def test_scenarios_as_admin_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a4, transition='stop')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_admin, self.a4)

    @browsing
    def test_scenarios_as_admin_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a4, transition='begin')
        api.content.transition(obj=self.a4, transition='finish')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_admin, self.a4)

    # pst editor -------------------------------------------------------------------------------------------------------
    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a4, transition='back_to_created')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a4)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_editor, self.a4)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a4, transition='begin')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.a4)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a4, transition='stop')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_editor, self.a4)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a4, transition='begin')
        api.content.transition(obj=self.a4, transition='finish')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_editor, self.a4)

    # manager ----------------------------------------------------------------------------------------------------------
    @browsing
    def test_scenarios_as_manager_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a4, transition='back_to_created')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.a4)

    @browsing
    def test_scenarios_as_manager_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.manager, self.a4)

    @browsing
    def test_scenarios_as_manager_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a4, transition='begin')
        state = api.content.get_state(obj=self.a4)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.a4)

    # ------------------------------------------------------------------------------------------------------------------
    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor clicks on "Split budget lines between multiple instances"
        self.step_2(browser)  # The system displays budget split view
        self.step_3(browser)  # The actor fairly shares the percentage
        self.step_4(browser, context)  # The system updates summarized fields and save changes with "Modify changes"

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays budget split view."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Répartition des budgets entre les différentes actions', heading.text)

    def step_3(self, browser):
        """The actor fairly shares the percentage."""
        form = browser.forms['form']
        fields = form.values
        fields['form.widgets.budget_split.0.widgets.percentage'] = u"50,0"
        fields['form.widgets.budget_split.1.widgets.percentage'] = u"50,0"
        form.find_button_by_label('Enregistrer').click()

    def step_4(self, browser, context):
        """The system updates summarized fields and save changes with "Modify changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Répartition des budgets entre les différentes actions', heading.text)
        statusmessages.assert_message(u'Répartition des budgets enregistrée')
        self.assertEqual(get_global_budget_infos(context.aq_parent),
                         {'europe': 18900.0, 'wallonie': 2500.0, 'federation-wallonie-bruxelles': 2438.0,
                          'province': 4111.0, 'ville': 107.5})
        self.assertEqual(get_global_budget_infos(context.aq_parent.aq_parent),
                         {'europe': 20091.0, 'wallonie': 3900.0, 'federation-wallonie-bruxelles': 4112.5,
                          'province': 4111.0, 'ville': 553.0})
