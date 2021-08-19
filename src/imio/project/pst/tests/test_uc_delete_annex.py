# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """selection_infos_annexe."""
    browser.open(context, view='iconifiedcategory')


def step_3(browser):
    """The actor click on delete button."""
    browser.open(browser.context.absolute_url() + '/annex_test/delete_confirmation')


def step_5(browser):
    """The actor click on delete button."""
    browser.find_button_by_label('Supprimer').click()
    # write browser contents
    # with open('browser_contents', 'w') as f:
    #     f.write(browser.contents)


def step_5a(browser):
    """The actor click on cancel button."""
    browser.css('#form-buttons-cancel').first.click()


def step_6(browser):
    """The system delete annex and back on the parent with deletion info."""
    statusmessages.assert_message(u'Annex test a été supprimé.')


class TestDeleteAnnex(FunctionalTestCase):
    """Use case tests.
    Name: Delete an annex
    Actor(s): pst admin
    Goal: allows actors to delete an annex
    Author: Franck Ngaha
    Created: 18/08/2021
    Updated: 19/08/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst project space in state (internally_published)
    - a pst admin in the context of a strategic objective in anyone of all his states (created, ongoing, achieved)
    - a pst admin in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - a pst admin in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst admin in the context of a pst sub action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    """

    def setUp(self):
        super(TestDeleteAnnex, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        # scenarios
        self.scenarios = [
            'main_scenario',
        ]

    @browsing
    def test_scenarios_as_admin_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a3)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.pst_admin, self.a3)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor select infos of annex
        self.step_2(browser)  # The system displays category view
        step_3(browser)  # The actor click on delete button
        self.step_4(browser)  # The system displays the deletion confirmation view
        step_5(browser)  # The actor click on delete button
        step_6(browser)  # The system delete annex and back to the context

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays category view."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Eléments catégorisés', heading.text)

    def step_4(self, browser):
        """The system displays the deletion confirmation view."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Voulez-vous réellement supprimer cet élément ?', heading.text)

    def step_6a(self, browser, context):
        """The system displays the annex view."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('annex_test.pdf', heading.text)
