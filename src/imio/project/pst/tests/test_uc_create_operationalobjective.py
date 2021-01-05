# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase


def step_3a(browser):
    """The user cancel the form."""
    form = browser.forms['form']
    form.find_button_by_label('Annuler').click()


def step_3c(browser):
    """The user fills in the fields but omit mandatory fields and save."""
    form = browser.forms['form']
    form.find_button_by_label('Sauvegarder').click()


def preconditions(browser, user):
    """Login as user."""
    browser.login(username=user['username'], password=user['password']).open()


class TestCreateOperationalObjective(FunctionalTestCase):
    """Test use case.
    Name: Create an operational objective
    Actor(s): pst_editors, admin
    Description: The creation of an operational objective must be possible for a pst editor and an administrator
    Author: Franck Ngaha
    Created: 15/10/2020
    Updated: 05/01/2021
    Preconditions: The user must be authenticated as a pst editor or administrator
    Start: The user is on the view of a strategic objective
    """

    def setUp(self):
        super(TestCreateOperationalObjective, self).setUp()
        self.pst_admin = {'username': 'pstadmin', 'password': self.password}
        self.pst_editor = {'username': 'psteditor', 'password': self.password}
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_1 = self.pst['etre-une-commune-qui-offre-un-service-public-moderne-efficace-et-efficient']

    @browsing
    def test_main_scenario_as_admin(self, browser):
        self.main_scenario(browser, self.pst_admin)

    @browsing
    def test_main_scenario_as_pst_editor(self, browser):
        self.main_scenario(browser, self.pst_editor)

    @browsing
    def test_alternative_scenario_3a_as_admin(self, browser):
        self.alternative_scenario_3a(browser, self.pst_admin)

    @browsing
    def test_alternative_scenario_3a_as_pst_editor(self, browser):
        self.alternative_scenario_3a(browser, self.pst_editor)

    @browsing
    def test_alternative_scenario_3b_as_admin(self, browser):
        self.alternative_scenario_3b(browser, self.pst_admin)

    @browsing
    def test_alternative_scenario_3b_as_pst_editor(self, browser):
        self.alternative_scenario_3b(browser, self.pst_editor)

    @browsing
    def test_exceptional_scenario_3c_as_admin(self, browser):
        self.exceptional_scenario_3c(browser, self.pst_admin)

    @browsing
    def test_exceptional_scenario_3c_as_pst_editor(self, browser):
        self.exceptional_scenario_3c(browser, self.pst_editor)

    def main_scenario(self, browser, user):
        preconditions(browser, user)  # Login as user
        self.start_up(browser)  # Open (OS.1)
        self.step_1(browser)  # The user adds operational objective
        self.step_2(browser)  # The system calculates default values and displays the form
        self.step_3(browser)  # The user fills in fields and save
        self.step_4(browser)  # The system creates and displays the operational objective

    def alternative_scenario_3a(self, browser, user):
        """The user cancel the form."""
        preconditions(browser, user)
        self.start_up(browser)
        self.step_1(browser)
        self.step_2(browser)
        step_3a(browser)  # The user cancel the form
        self.step_4a(browser)  # The system back to the previous page with "Addition canceled" Info

    def alternative_scenario_3b(self, browser, user):
        """The user fills in the fields but not the deadline and save."""
        preconditions(browser, user)
        self.start_up(browser)
        self.step_1(browser)
        self.step_2(browser)
        self.step_3b(browser)  # The user fills in the fields but not the deadline
        self.step_4b(browser)  # The system creates the operational objective with warning message

    def exceptional_scenario_3c(self, browser, user):
        """The user fills in the fields but omit a mandatory field and save."""
        preconditions(browser, user)
        self.start_up(browser)
        self.step_1(browser)
        self.step_2(browser)
        step_3c(browser)  # The user fills in the fields but omit mandatory fields
        self.step_4c(browser)  # system warn, (back to the step 2)

    def start_up(self, browser):
        """Open (OS.1)."""
        browser.open(self.os_1)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(
            "Etre une commune qui offre un service public moderne, efficace et efficient (OS.1)".decode('utf8'),
            heading.text)

    def step_1(self, browser):
        """The user adds operationalobjactive."""
        browser.open(self.os_1.absolute_url() + '/++add++operationalobjective')

    def step_2(self, browser):
        """
        The system calculates the default values of the 'Categories' and 'Plans' fields,
        pre-populates and displays add action form
        """
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Objectif opérationnel', heading.text)
        form = browser.forms['form']
        fields = form.values
        categories = fields[self.categories_form_widget_name]
        plans = fields[self.plan_form_widget_name]
        self.assertTrue(categories.__eq__(set(self.os_1.categories)))
        self.assertTrue(plans.__eq__(set(self.os_1.plan)))

    def step_3(self, browser):
        """The user fills in the form and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_form_widget_name] = u"Titre"
        fields[self.description_form_widget_name] = u"Description"
        fields[self.result_indicator_label_form_widget_name] = u"Libellé"
        fields[self.result_indicator_value_form_widget_name] = u"100"
        fields[self.result_indicator_reached_value_form_widget_name] = u"50"
        fields[self.result_indicator_year_form_widget_name] = u"2020"
        fields[self.priority_form_widget_name] = u"2"
        fields[self.planned_end_date_day_form_widget_name] = u"25"
        fields[self.planned_end_date_month_form_widget_name] = u"11"
        fields[self.planned_end_date_year_form_widget_name] = u"2020"
        fields[self.representative_responsible_form_widget_name] = [self.echevins_config['bourgmestre']]
        fields[self.administrative_responsible_form_widget_name] = [
            self.services_config['service-informatique'].decode('utf8')]
        fields[self.manager_form_widget_name] = [self.services_config['service-informatique'].decode('utf8')]
        fields[self.extra_concerned_people_form_widget_name] = u"Partenaires externes"
        fields[self.budget_type_form_widget_name] = u"wallonie"
        fields[self.budget_year_form_widget_name] = u"2021"
        fields[self.budget_amount_form_widget_name] = u"10000,0"
        fields[self.budget_comments_form_widget_name] = u"Commentaires sur le financement/budget"
        fields[self.sdgs_form_widget_name] = [u"11"]
        fields[self.observation_form_widget_name] = u"Constat"
        fields[self.comments_form_widget_name] = u"Commentaires"
        form.find_button_by_label('Sauvegarder').click()

    def step_3b(self, browser):
        """The user fills in the fields but not the deadline and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_form_widget_name] = u"Titre"
        fields[self.representative_responsible_form_widget_name] = [self.echevins_config['bourgmestre']]
        fields[self.administrative_responsible_form_widget_name] = [
            self.services_config['service-informatique'].decode('utf8')]
        fields[self.manager_form_widget_name] = [self.services_config['service-informatique'].decode('utf8')]
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser):
        """The system creates and displays the element with "Saved changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (OO.24)', heading.text)
        statusmessages.assert_message(u'Elément créé')

    def step_4a(self, browser):
        """The system back to the previous page with "Addition canceled" Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(
            "Etre une commune qui offre un service public moderne, efficace et efficient (OS.1)".decode('utf8'),
            heading.text)
        statusmessages.assert_message(u"Ajout annulé")

    def step_4b(self, browser):
        """
        The system searches for the max planned end date of the contained items,
        adds it to the operational objective metadata,
        creates and displays the element with a warning message
        """
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (OO.24)', heading.text)
        statusmessages.assert_message(u"Elément créé")

    def step_4c(self, browser):
        """The system displays warnings, (Back to the step 2)."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Ajouter Objectif opérationnel', heading.text)
        self.assertTrue('Champ obligatoire' in browser.contents)
        statusmessages.assert_message(u"Il y a des erreurs.")
