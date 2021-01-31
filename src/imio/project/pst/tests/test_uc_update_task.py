# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
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


class TestUpdateTask(FunctionalTestCase):
    """Use case tests.
    Name: Update task
    Actor(s): pst admin, pst editors, validateur, editeur
    Goal: allows actors to update a task
    Author: Franck Ngaha
    Created: 27/01/2021
    Updated: 27/01/2021
    Preconditions: The actor must be authenticated in a given specific context :
    - a pst admin in the context of a task in anyone of all his states
    (created, to_assign, to_do, in_progress, realized, closed)
    - a pst editor in the context of a task in anyone of all his states
    (created, to_assign, to_do, in_progress, realized, closed)
    - a validateur in the context of a task in anyone of all his states
    (created, to_assign, to_do, in_progress, realized, closed)
    - an editeur in the context of a task in following states (to_do, in_progress, realized)
    """

    def setUp(self):
        super(TestUpdateTask, self).setUp()
        # Actors
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.validateur = {'username': 'agent', 'password': self.password}
        self.editeur = {'username': 'agent', 'password': self.password}
        # Contexts
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_10 = self.pst[
            'etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-de-serre-afin-dassu'
            'rer-le-developpement-durable']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']
        self.a_16 = self.oo_15['reduire-la-consommation-energetique-de-ladministration-communale']
        self.sa_17 = self.a_16['realiser-un-audit-energetique-du-batiment']
        self.t1 = self.sa_17['ecrire-le-cahier-des-charges']
        # scenarios
        self.scenarios = [
            'main_scenario',
            'alternative_scenario_3a',
            'alternative_scenario_3b',
            'alternative_scenario_3c',
        ]

    @browsing
    def test_scenarios_as_admin_in_task_created(self, browser):
        api.content.transition(obj=self.t1, transition='back_in_created')
        state = api.content.get_state(obj=self.t1)
        self.assertEqual(state, 'created')
        self.call_scenarios(browser, self.pst_admin, self.t1)

    @browsing
    def test_scenarios_as_admin_in_task_to_assign(self, browser):
        state = api.content.get_state(obj=self.t1)
        self.assertEqual(state, 'to_assign')
        self.call_scenarios(browser, self.pst_admin, self.t1)

    @browsing
    def test_scenarios_as_admin_in_task_to_do(self, browser):
        self.t1.assigned_user = 'agent'
        api.content.transition(obj=self.t1, transition='do_to_do')
        state = api.content.get_state(obj=self.t1)
        self.assertEqual(state, 'to_do')
        self.call_scenarios(browser, self.pst_admin, self.t1)

    @browsing
    def test_scenarios_as_admin_in_task_in_progress(self, browser):
        self.t1.assigned_user = 'agent'
        api.content.transition(obj=self.t1, transition='do_to_do')
        api.content.transition(obj=self.t1, transition='do_in_progress')
        state = api.content.get_state(obj=self.t1)
        self.assertEqual(state, 'in_progress')
        self.call_scenarios(browser, self.pst_admin, self.t1)

    @browsing
    def test_scenarios_as_admin_in_task_realized(self, browser):
        self.t1.assigned_user = 'agent'
        api.content.transition(obj=self.t1, transition='do_to_do')
        api.content.transition(obj=self.t1, transition='do_realized')
        state = api.content.get_state(obj=self.t1)
        self.assertEqual(state, 'realized')
        self.call_scenarios(browser, self.pst_admin, self.t1)

    @browsing
    def test_scenarios_as_admin_in_task_closed(self, browser):
        self.t1.assigned_user = 'agent'
        api.content.transition(obj=self.t1, transition='do_to_do')
        api.content.transition(obj=self.t1, transition='do_realized')
        api.content.transition(obj=self.t1, transition='do_closed')
        state = api.content.get_state(obj=self.t1)
        self.assertEqual(state, 'closed')
        self.call_scenarios(browser, self.pst_admin, self.t1)

    def call_scenarios(self, browser, actor, context):
        for scenario in self.scenarios:
            self.__getattribute__(scenario)(browser, actor, context)

    def main_scenario(self, browser, actor, context):
        preconditions(browser, actor)  # Login as actor
        self.start_up(browser, context)  # Open context
        step_1(browser, context)  # The actor opens edit form
        self.step_2(browser)  # The system displays task's edit form
        self.step_3(browser)  # The actor update fields and save
        self.step_4(browser)  # The system save changes with "Modify changes" info success

    def alternative_scenario_3a(self, browser, actor, context):
        """The actor cancel the form."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        step_3a(browser)  # The actor cancels the form
        self.step_4a(browser, context)  # The system back to the previous page with "Modification canceled" Info

    def alternative_scenario_3b(self, browser, actor, context):
        """The actor remove the deadline and save."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        self.step_3b(browser)  # The actor removes the deadline
        self.step_4b(browser)  # The system displays a warning message

    def alternative_scenario_3c(self, browser, actor, context):
        """The actor fills a deadline greater than one of their parents."""
        preconditions(browser, actor)
        self.start_up(browser, context)
        step_1(browser, context)
        self.step_2(browser)
        self.step_3c(browser)  # The actor fills a greater deadline
        self.step_4c(browser, context)  # The system updates element with warning message

    def start_up(self, browser, context):
        """Open context."""
        browser.open(context)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)

    def step_2(self, browser):
        """The system displays task's edit form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Editer Tâche', heading.text)

    def step_3(self, browser):
        """The actor update fields and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_form_widget_name] = u'Titre'
        form.find_button_by_label('Sauvegarder').click()

    def step_3b(self, browser):
        """The actor remove the deadline and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.due_date_day_form_widget_name] = u''
        fields[self.due_date_month_form_widget_name] = u''
        fields[self.due_date_year_form_widget_name] = u''
        form.find_button_by_label('Sauvegarder').click()

    def step_3c(self, browser):
        """
        The actor fills a deadline (31/07/2020) greater than one of their parents.
        parent deadline :
         (oo_15, 31/12/2024)
             (a_16, 30/06/2024)
                 (sa_17, 30/06/2020)
                      (t1, 30/04/2020)
        """
        form = browser.forms['form']
        fields = form.values
        fields[self.due_date_day_form_widget_name] = u'31'
        fields[self.due_date_month_form_widget_name] = u'7'
        fields[self.due_date_year_form_widget_name] = u'2020'
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser):
        """The system save changes with "Modify changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre', heading.text)
        statusmessages.assert_message(u'Modifications sauvegardées')
        catalog = api.portal.get_tool(name='portal_catalog')
        mirror_t1_brain = catalog(path={"query": '/plone/pst/etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords'
                                                 '-de-reductions-des-gaz-a-effet-de-serre-afin-dassurer-le-developpem'
                                                 'ent-durable/reduire-la-consommation-energetique-des-batiments-commu'
                                                 'naux-de-20-dici-2024/reduire-la-consommation-energetique-de-ladmini'
                                                 'stration-communale/realiser-un-audit-energetique-du-batiment/ecrire'
                                                 '-le-cahier-des-charges'})[0]
        t1_brain = catalog(path={"query": '/plone/pst/etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-re'
                                          'ductions-des-gaz-a-effet-de-serre-afin-dassurer-le-developpement-durable/'
                                          'reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-20'
                                          '24/reduire-la-consommation-energetique-du-hangar-communal/realiser-un-aud'
                                          'it-energetique-du-batiment/ecrire-le-cahier-des-charges'})[0]
        self.assertEqual(t1_brain.Title, mirror_t1_brain.Title)

    def step_4a(self, browser, context):
        """The system back to the previous page with 'Modification canceled' Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title().decode('utf8'), heading.text)
        statusmessages.assert_message(u'Modification annulée')

    def step_4b(self, browser):
        """The system displays a warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre', heading.text)
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance n'est pas renseignée sur cet élément."]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')

    def step_4c(self, browser, context):
        """The system updates element with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(context.Title(), heading.text)
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance de cet élément est supérieure à au moins une de ses parents."]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-ITask-due_date').text, ['31/07/2020'])
