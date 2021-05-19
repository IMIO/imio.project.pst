# -*- coding: utf-8 -*-

from ftw.testbrowser import browsing
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


class TestGenerateDetailedReport(FunctionalTestCase):
    """Use case tests.
    Name: Generate a "Follow-up" report
    Actor(s): pst admin, pst editors, pst reader
    Goal: allows actors to generate a "Follow-up" report
    Author: Franck Ngaha
    Created: 18/05/2021
    Updated: 18/05/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst project space in state (internally_published)
    - a pst admin in the context of an strategic objective in anyone of all his states (created, ongoing, achieved))
    - a pst admin in the context of an operational objective in anyone of all his states (created, ongoing, achieved))
    - a pst admin in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst editor in the context of a pst project space in state (internally_published)
    - a pst editor in the context of an strategic objective in anyone of all his states (created, ongoing, achieved))
    - a pst editor in the context of an operational objective in anyone of all his states (created, ongoing, achieved))
    - a pst editor in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst reader in the context of a pst project space in state (internally_published)
    - a pst reader in the context of an strategic objective in anyone of all his states (created, ongoing, achieved))
    - a pst reader in the context of an operational objective in anyone of all his states (created, ongoing, achieved))
    - a pst reader in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    """

    def setUp(self):
        super(TestGenerateDetailedReport, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.pst_reader = {'username': 'pstreader', 'password': self.password}
        # Context
        self.template = self.pst.templates.follow
        # scenarios
        self.scenarios = [
            'main_scenario',
        ]

    @browsing
    def test_scenarios_as_admin_in_pst_project_space_internally_published(self, browser):
        state = api.content.get_state(obj=self.pst)
        self.assertEqual(state, 'internally_published')
        self.call_scenarios(browser, self.pst_admin, self.pst)

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
    def test_scenarios_as_admin_in_strategic_objective_achieved(self, browser):
        api.content.transition(obj=self.os1, transition='achieve')
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_admin, self.os1)

    @browsing
    def test_scenarios_as_admin_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.oo2)

    @browsing
    def test_scenarios_as_admin_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.oo2)

    @browsing
    def test_main_scenario_as_admin_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo2, transition='achieve')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_admin, self.oo2)

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
    def test_scenarios_as_admin_in_pst_sub_action_created(self, browser):
        api.content.transition(obj=self.sa17, transition='back_to_created')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.sa17)

    @browsing
    def test_scenarios_as_admin_in_pst_sub_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_admin, self.sa17)

    @browsing
    def test_scenarios_as_admin_in_pst_sub_action_ongoing(self, browser):
        api.content.transition(obj=self.sa17, transition='begin')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_admin, self.sa17)

    @browsing
    def test_scenarios_as_admin_in_pst_sub_action_stopped(self, browser):
        api.content.transition(obj=self.sa17, transition='stop')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_admin, self.sa17)

    @browsing
    def test_scenarios_as_admin_in_pst_sub_action_terminated(self, browser):
        api.content.transition(obj=self.sa17, transition='begin')
        api.content.transition(obj=self.sa17, transition='finish')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_admin, self.sa17)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_project_space_internally_published(self, browser):
        state = api.content.get_state(obj=self.pst)
        self.assertEqual(state, 'internally_published')
        self.call_scenarios(browser, self.pst_editor, self.pst)

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
    def test_scenarios_as_pst_editor_in_strategic_objective_achieved(self, browser):
        api.content.transition(obj=self.os1, transition='achieve')
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_editor, self.os1)

    @browsing
    def test_scenarios_as_pst_editor_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_editor, self.oo2)

    @browsing
    def test_scenarios_as_pst_editor_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.oo2)

    @browsing
    def test_main_scenario_as_pst_editor_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo2, transition='achieve')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_editor, self.oo2)

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
    def test_scenarios_as_pst_editor_in_pst_sub_action_created(self, browser):
        api.content.transition(obj=self.sa17, transition='back_to_created')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_editor, self.sa17)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_sub_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_editor, self.sa17)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_sub_action_ongoing(self, browser):
        api.content.transition(obj=self.sa17, transition='begin')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_editor, self.sa17)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_sub_action_stopped(self, browser):
        api.content.transition(obj=self.sa17, transition='stop')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_editor, self.sa17)

    @browsing
    def test_scenarios_as_pst_editor_in_pst_sub_action_terminated(self, browser):
        api.content.transition(obj=self.sa17, transition='begin')
        api.content.transition(obj=self.sa17, transition='finish')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_editor, self.sa17)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_project_space_internally_published(self, browser):
        state = api.content.get_state(obj=self.pst)
        self.assertEqual(state, 'internally_published')
        self.call_scenarios(browser, self.pst_reader, self.pst)

    @browsing
    def test_scenarios_as_pst_reader_in_strategic_objective_created(self, browser):
        api.content.transition(obj=self.os1, transition='back_to_created')
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_reader, self.os1)

    @browsing
    def test_scenarios_as_pst_reader_in_strategic_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_reader, self.os1)

    @browsing
    def test_scenarios_as_pst_reader_in_strategic_objective_achieved(self, browser):
        api.content.transition(obj=self.os1, transition='achieve')
        state = api.content.get_state(obj=self.os1)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_reader, self.os1)

    @browsing
    def test_scenarios_as_pst_reader_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_reader, self.oo2)

    @browsing
    def test_scenarios_as_pst_reader_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_reader, self.oo2)

    @browsing
    def test_main_scenario_as_pst_reader_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo2, transition='achieve')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.pst_reader, self.oo2)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a16, transition='back_to_created')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.a16)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_reader, self.a16)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_reader, self.a16)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a16, transition='stop')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_reader, self.a16)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        api.content.transition(obj=self.a16, transition='finish')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_reader, self.a16)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_sub_action_created(self, browser):
        api.content.transition(obj=self.sa17, transition='back_to_created')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_reader, self.sa17)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_sub_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_reader, self.sa17)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_sub_action_ongoing(self, browser):
        api.content.transition(obj=self.sa17, transition='begin')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.pst_reader, self.sa17)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_sub_action_stopped(self, browser):
        api.content.transition(obj=self.sa17, transition='stop')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.pst_reader, self.sa17)

    @browsing
    def test_scenarios_as_pst_reader_in_pst_sub_action_terminated(self, browser):
        api.content.transition(obj=self.sa17, transition='begin')
        api.content.transition(obj=self.sa17, transition='finish')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.pst_reader, self.sa17)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        self.step_1(browser, context)  # The actor clicks on Suivi"
        self.step_2(browser)  # The system creates the odt file and distributes it

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_1(self, browser, context):
        """The actor clicks on "Détaillé"."""
        url = 'document-generation?template_uid={}&output_format=odt'.format(self.template.UID())
        browser.open(context, view=url)
        # write browser contents
        # with open('browser_contents', 'w') as f:
        #     f.write(browser.contents)

    def step_2(self, browser):
        """The system creates the odt file and distributes it."""
        self.assertEqual('application/vnd.oasis.opendocument.text', browser.contenttype)
