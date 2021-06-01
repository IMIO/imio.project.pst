# -*- coding: utf-8 -*-

from ftw.testbrowser import browsing
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


class TestGenerateManagerFollowReport(FunctionalTestCase):
    """Use case tests.
    Name: Generate a manager follow-up report
    Actor(s): manager
    Goal: allows actors to generate an manager follow-up report
    Author: Franck Ngaha
    Created: 31/05/2021
    Updated: 01/06/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a manager in the context of a pst project space in state (internally_published)
    """

    def setUp(self):
        super(TestGenerateManagerFollowReport, self).setUp()
        # Actors
        self.manager = {'username': 'agent', 'password': self.password}
        # Context
        self.template = self.pst.templates['dmanagers']
        self.i_am_manager_uid = self.portal.pst.pstactions['i-am-manager'].UID()
        # scenarios
        self.scenarios = [
            'main_scenario',
        ]

    @browsing
    def test_scenarios_as_manager_in_pst_project_space_internally_published(self, browser):
        state = api.content.get_state(obj=self.pst)
        self.assertEqual(state, 'internally_published')
        self.call_scenarios(browser, self.manager, self.pst)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        self.step_1(browser, context)  # The actor clicks on "Dont je suis gestionnaire"
        self.step_2(browser)  # The system display search results
        self.step_3(browser, context)  # The actor clicks on "Suivi gestionnaire"
        self.step_4(browser)  # The system creates the odt file and distributes it

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_1(self, browser, context):
        """The actor clicks on "Dont je suis gestionnaire"."""
        url = 'http://nohost/plone/pst/pstactions?no_redirect=1#c0=sortable_title&c1={}&c3=20'.format(
            self.i_am_manager_uid)
        browser.open(url)
        # write browser contents
        # with open('browser_contents', 'w') as f:
        #     f.write(browser.contents)

    def step_2(self, browser):
        """The system display search results."""
        heading = browser.css('.documentFirstHeading').first
        self.assertIn(heading.text, "Actions (sous-)")

    def step_3(self, browser, context):
        """The actor clicks on "Suivi gestionnaires"."""
        url = 'document-generation?template_uid={}&output_format=ods'.format(self.template.UID())
        browser.open(browser.context, view=url)
        # write browser contents
        # with open('browser_contents', 'w') as f:
        #     f.write(browser.contents)

    def step_4(self, browser):
        """The system creates the odt file and distributes it."""
        self.assertEqual('application/vnd.oasis.opendocument.spreadsheet', browser.contenttype)
