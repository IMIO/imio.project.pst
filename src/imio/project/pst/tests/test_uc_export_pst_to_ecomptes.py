# -*- coding: utf-8 -*-

from ftw.testbrowser import browsing
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor clicks on "Export to eComptes"."""
    browser.open(context, view='export_as_xml')


class TestExportPstToEcompte(FunctionalTestCase):
    """Use case tests.
    Name: Export PST to eComptes
    Actor(s): pst admin, pst editors
    Goal: allows actors to create an an xml export to Ecompte
    Author: Franck Ngaha
    Created: 04/02/2021
    Updated: 05/02/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst project space in state (internally_published)
    - a pst editor in the context of a pst project space in state (internally_published)
    """

    def setUp(self):
        super(TestExportPstToEcompte, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
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
        step_1(browser, context)  # The actor clicks on "Export to eComptes"
        self.step_2(browser)  # The system creates the xml file and distributes it

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system creates the xml file and distributes it."""
        self.assertIn('text/xml', browser.contenttype)
        self.assertEqual(browser.document.xpath('/dataroot/Identifiants/TypeAdmin')[0].text, 'AC')
