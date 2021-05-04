# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

from ftw.testbrowser import browsing
from imio.project.pst.testing import FunctionalTestCase
from plone import api
from zope.annotation import IAnnotations


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser):
    """The actor clicks on "Import from eComptes"."""
    browser.click_on("Import depuis eComptes".decode('utf8'))


class TestImportPstFromEcompte(FunctionalTestCase):
    """Use case tests.
    Name: Import PST from eComptes
    Actor(s): pst admin, pst editors
    Goal: allows actors to integrate an eComptes xml export into PST
    Author: Franck Ngaha
    Created: 27/04/2021
    Updated: 04/05/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst project space in state (internally_published)
    - a pst editor in the context of a pst project space in state (internally_published)
    """

    def setUp(self):
        super(TestImportPstFromEcompte, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
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
        step_1(browser)  # The actor clicks on "Import from eComptes"
        self.step_2(browser)  # The system displays import data from eComptes form
        self.step_3(browser)  # The actor selects and imports the eComptes xml file
        self.step_4()  # The system integrates analytics budgets

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays import data from eComptes form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Importer des données depuis eComptes', heading.text)

    def step_3(self, browser):
        """The actor selects and imports the eComptes xml file.."""
        xml_file = '../../src/imio.project.pst/src/imio/project/pst/model/demo_import_pst_from_ecomptes_201805V1.xsd'
        mytree = ET.parse(xml_file)
        myroot = mytree.getroot()
        # Update ElementId
        self.assertEqual(myroot[1][1][0][10][1][10][1][13][1].get('ElementId'), 'b07ec94c0e804690a9ef971db84e12b1')
        myroot[1][1][0][10][1][10][1][13][1].set('ElementId', self.sa17.UID())
        mytree.write('ecomptes_pst.xml')
        # select xml file
        file_field = browser.find(u'Document XML exporté depuis eComptes')
        with open('ecomptes_pst.xml', 'r') as f:
            file_field.set('value', (f.read(), 'ecomptes_pst.xml'))
        # import xml file
        browser.find_button_by_label('Importer').click()
        # write browser contents
        # with open('browser_contents', 'w') as f:
        #     f.write(browser.contents)

    def step_4(self):
        """The system integrates analytics budgets.."""
        self.assertEqual(self.sa17.analytic_budget, [
            {'service': u'O', 'title': u'Réaliser un audit énergétique du bâtiment', 'btype': u'D',
             'amount': 500.0, 'year': 2019, 'article': u'xxx/wal-17.2019'},
            {'service': u'O', 'title': u'Réaliser un audit énergétique du bâtiment', 'btype': u'D',
             'amount': 500.0, 'year': 2020, 'article': u'xxx/wal-17.2020'},
            {'service': u'O', 'title': u'Réaliser un audit énergétique du bâtiment', 'btype': u'D',
             'amount': 500.0, 'year': 2021, 'article': u'xxx/wal-17.2021'},
            {'service': u'O', 'title': u'Réaliser un audit énergétique du bâtiment', 'btype': u'D',
             'amount': 500.0, 'year': 2022, 'article': u'xxx/wal-17.2022'}])
