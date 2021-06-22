# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from plone import api


def preconditions(browser, actor):
    """Login as actor."""
    browser.login(username=actor['username'], password=actor['password']).open()


def step_1(browser, context):
    """The actor adds annex."""
    browser.open(context.absolute_url() + '/++add++File')


def step_3a(browser):
    """The actor cancel the form."""
    browser.css('#form-buttons-cancel').first.click()


def step_3b(browser):
    """The actor fills in the fields but omit mandatory fields and save."""
    form = browser.forms['form']
    form.find_button_by_label('Sauvegarder').click()


class TestCreateAnnex(FunctionalTestCase):
    """Use case tests.
    Name: Create an annex
    Actor(s): pst admin, pst editors, administrative responsible, manager
    Goal: allows actors to create an annex
    Author: Franck Ngaha
    Created: 21/06/2021
    Updated: 22/06/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a pst project space in state (internally_published)
    - a pst admin in the context of a strategic objective in anyone of all his states (created, ongoing, achieved)
    - a pst admin in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - a pst admin in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst admin in the context of a pst sub action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst editor in the context of a pst project space in state (internally_published)
    - a pst editor in the context of a strategic objective in anyone of all his states (created, ongoing, achieved)
    - a pst editor in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - a pst editor in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a pst editor in the context of a pst sub action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - an administrative responsible in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - a manager in the context of an operational objective in anyone of all his states (created, ongoing, achieved)
    - a manager in the context of a pst action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    - a manager in the context of a pst sub action in anyone of all his states
    (created, ongoing, stopped, terminated, to_be_scheduled)
    """

    def setUp(self):
        super(TestCreateAnnex, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.adm_resp = {'username': 'chef', 'password': self.password}
        self.manager = {'username': 'agent', 'password': self.password}
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'exceptional_scenario_3b'
        ]

    # admin ------------------------------------------------------------------------------------------------------------
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

    # pst editor -------------------------------------------------------------------------------------------------------
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
        self.call_scenarios(browser, self.pst_editor, self.a16)

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

    # administrative responsible ---------------------------------------------------------------------------------------
    @browsing
    def test_scenarios_as_adm_resp_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.adm_resp, self.oo2)

    @browsing
    def test_scenarios_as_adm_resp_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.adm_resp, self.oo2)

    @browsing
    def test_main_scenario_as_adm_resp_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo2, transition='achieve')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.adm_resp, self.oo2)

    # manager ----------------------------------------------------------------------------------------------------------
    @browsing
    def test_scenarios_as_manager_in_operational_objective_created(self, browser):
        api.content.transition(obj=self.oo2, transition='back_to_created')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.oo2)

    @browsing
    def test_scenarios_as_manager_in_operational_objective_ongoing(self, browser):
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.oo2)

    @browsing
    def test_main_scenario_as_manager_in_operational_objective_achieved(self, browser):
        api.content.transition(obj=self.oo2, transition='achieve')
        state = api.content.get_state(obj=self.oo2)
        self.assertEqual(state, 'achieved')
        self.call_scenarios(browser, self.manager, self.oo2)

    @browsing
    def test_scenarios_as_manager_in_pst_action_created(self, browser):
        api.content.transition(obj=self.a16, transition='back_to_created')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.manager, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_ongoing(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_stopped(self, browser):
        api.content.transition(obj=self.a16, transition='stop')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.manager, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_action_terminated(self, browser):
        api.content.transition(obj=self.a16, transition='begin')
        api.content.transition(obj=self.a16, transition='finish')
        state = api.content.get_state(obj=self.a16)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.manager, self.a16)

    @browsing
    def test_scenarios_as_manager_in_pst_sub_action_created(self, browser):
        api.content.transition(obj=self.sa17, transition='back_to_created')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.manager, self.sa17)

    @browsing
    def test_scenarios_as_manager_in_pst_sub_action_to_be_scheduled(self, browser):
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'to_be_scheduled')
        self.call_scenarios(browser, self.manager, self.sa17)

    @browsing
    def test_scenarios_as_manager_in_pst_sub_action_ongoing(self, browser):
        api.content.transition(obj=self.sa17, transition='begin')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'ongoing')
        self.call_scenarios(browser, self.manager, self.sa17)

    @browsing
    def test_scenarios_as_manager_in_pst_sub_action_stopped(self, browser):
        api.content.transition(obj=self.sa17, transition='stop')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'stopped')
        self.call_scenarios(browser, self.manager, self.sa17)

    @browsing
    def test_scenarios_as_manager_in_pst_sub_action_terminated(self, browser):
        api.content.transition(obj=self.sa17, transition='begin')
        api.content.transition(obj=self.sa17, transition='finish')
        state = api.content.get_state(obj=self.sa17)
        self.assertEqual(state, 'terminated')
        self.call_scenarios(browser, self.manager, self.sa17)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor adds annex
        self.step_2(browser, context)  # The system displays the form
        self.step_3(browser)  # The actor fills in fields and save
        self.step_4(browser)  # The system creates and displays annex

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

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser, context):
        """The system displays add file form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Fichier', heading.text)

    def step_3(self, browser):
        """The actor fills in the form and save."""
        annex_file = '../../src/imio.project.pst/src/imio/project/pst/model/annex_test.pdf'
        with open(annex_file, 'r') as pdf:
            browser.fill({self.file_form_widget_name: pdf}).find_button_by_label('Sauvegarder').click()
        # write browser contents
        # with open('browser_contents', 'w') as f:
        #     f.write(browser.contents)

    def step_4(self, browser):
        """The system creates and displays annex with "Saved changes" info success."""
        statusmessages.assert_message(u'Elément créé')
        browser.find('annex_test.pdf').click()
        self.assert_file_metadata(filename='annex_test.pdf',
                                  content_type='application/pdf',
                                  browser=browser)

    def step_4a(self, browser, context):
        """The system back to the previous page with "Addition canceled" Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u"Ajout annulé")

    def step_4b(self, browser):
        """The system displays warnings, (Back to the step 2)."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Fichier', heading.text)
        self.assertTrue('Champ obligatoire' in browser.contents)
        statusmessages.assert_message(u"Il y a des erreurs.")

    def assert_file_metadata(self, browser, filename, content_type):
        self.assertIn(
            browser.headers.get('Content-Disposition'),
            ('attachment; filename="%s"' % filename,
             'attachment; filename*=UTF-8\'\'%s' % filename))
        self.assertIn(browser.headers.get('Content-Type'), (
            '%s; charset=utf-8' % content_type,  # Zope 4
            '%s; charset=iso-8859-15' % content_type,  # mechanize download
            content_type,  # requests lib download
        ))
