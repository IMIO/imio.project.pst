# -*- coding: utf-8 -*-

from imio.project.pst.testing import FunctionalTestCase


class TestEncodeAnOperationalObjective(FunctionalTestCase):
    """
    Name: Encode an operational objective
    Actor(s): pst_editors, admin_resp
    Description: The encoding of an operational objective must be possible for a global editor,
                 an administrative manager as well as an administrator
    Author: Franck Ngaha
    Date: 10/15/2020
    Preconditions: The user must be authenticated as a global editor or administrative manager or administrator
    Start: The user is on the page of a strategic objective
    """

    def setUp(self):
        super(TestEncodeAnOperationalObjective, self).setUp()
        self.preconditions()

    def tearDown(self):
        self.logout()

    def test_scenario(self):
        self.start_up()
        self.step_1()  # user activates 'Add an item'
        self.step_2()  # system displays the list
        self.step_3()  # user selects 'Operational objective'
        self.step_4()  # system calculates default values
        self.step_5()  # user fills in fields and save
        self.step_6()  # system creates element

    def test_alternative_5a(self):
        """The user clicks on the "! Cancel" button."""
        self.start_up()
        self.step_1()  # user activates 'Add an item'
        self.step_2()  # system displays the list
        self.step_3()  # user selects 'Operational objective'
        self.step_4()  # system calculates default values
        self.step_5a()  # user cancel
        self.step_6a()  # system go back

    def test_exceptional_6a(self):
        """The system signals mandatory field completion errors (return to step 5)."""
        self.start_up()
        self.step_1()  # user activates 'Add an item'
        self.step_2()  # system displays the list
        self.step_3()  # user selects 'Operational objective'
        self.step_4()  # system calculates default values
        self.step_5b()  # user does not fill in required fields
        self.step_6b()  # system warn

    def preconditions(self):
        # The user must be authenticated as pst_editors or admin_resp or admin
        self.login('psteditor', self.password)

    def start_up(self):
        # The user is on a strategic objective page
        self.browser.open(self.portal.absolute_url())
        self.assertEqual(self.browser.title, 'Programme Strat\xc3\xa9gique Transversal 1.3 \xe2\x80\x94 Site')
        self.browser.getLink('PST 2019-2024').click()
        self.assertEqual(self.browser.title, 'PST 2019-2024 \xe2\x80\x94 Site')
        self.browser.getLink('Plan du PST').click()
        self.browser.getLink(
            'Etre une commune qui offre un service public moderne, efficace et efficient (OS.1)').click()
        self.assertEqual(
            self.browser.title,
            'Etre une commune qui offre un service public moderne, efficace et efficient (OS.1) \xe2\x80\x94 Site')

    def step_1(self):
        """The user activates the selection list 'Add an item'."""
        self.add_element_ctrl = self.browser.getControl(name='Add element')

    def step_2(self):
        """The system displays the selection list."""
        self.assertEqual(
            self.add_element_ctrl.displayOptions,
            ["Ajout d'un \xc3\xa9l\xc3\xa9ment", 'Fichier', 'Objectif op\xc3\xa9rationnel']
        )

    def step_3(self):
        """The user selects 'Operational objective'."""
        self.add_element_ctrl.displayValue = ['Objectif op\xc3\xa9rationnel']
        self.browser.open(self.add_element_ctrl.value[0])

    def step_4(self):
        """
        The system calculates the default values of the 'Categories' and 'Plans' fields,
        pre-populates and displays the form for editing an operational objective.
        """
        self.form = self.browser.getForm('form')
        parent_os_categories_value = self.portal['pst']['etre-une-commune-qui-offre-un-service-public-moderne-'
                                                        'efficace-et-efficient'].categories
        parent_os_plan_value = self.portal['pst']['etre-une-commune-qui-offre-un-service-public-moderne-efficace-et'
                                                  '-efficient'].plan
        oo_categories_value = self.form.getControl(name=self.categories_input_name).value
        oo_plan_value = self.form.getControl(name=self.plan_input_name).value
        self.assertEqual(oo_categories_value.sort(), parent_os_categories_value.sort())
        self.assertEqual(oo_plan_value.sort(), parent_os_plan_value.sort())

    def step_5(self):
        """The user fills in the fields and clicks on the 'Save' button."""
        self.form.getControl(name=self.title_input_name).value = 'Titre'
        self.form.getControl(name=self.description_input_name).value = 'Description'
        self.form.getControl(name=self.result_indicator_label_input_name).value = 'Libellé'
        self.form.getControl(name=self.result_indicator_value_input_name).value = '10'
        self.form.getControl(name=self.result_indicator_reached_value_input_name).value = '5'
        self.form.getControl(name=self.result_indicator_year_input_name).displayValue = ['2020']
        self.form.getControl(name=self.priority_input_name).displayValue = ['2']
        self.form.getControl(name=self.planned_end_date_day_input_name).displayValue = ['04']
        self.form.getControl(name=self.planned_end_date_month_input_name).displayValue = ['janvier']
        self.form.getControl(name=self.planned_end_date_year_input_name).displayValue = ['2021']
        self.form.getControl(name=self.representative_responsible_input_name).displayValue = ['bourgmestre']
        self.form.getControl(name=self.administrative_responsible_input_name).displayValue = ['Service Informatique']
        self.form.getControl(name=self.manager_input_name).displayValue = ['Service Informatique']
        self.form.getControl(name=self.extra_concerned_people_input_name).value = 'Partenaires externes'
        self.form.getControl(name=self.budget_type_input_name).value = ['wallonie']
        self.form.getControl(name=self.budget_year_input_name).displayValue = ['2021']
        self.form.getControl(name=self.budget_amount_input_name).value = '10000,0'
        self.form.getControl(name=self.budget_comments_input_name).value = 'Commentaires sur le financement/budget'
        self.form.getControl(name=self.sdgs_input_name).displayValue = [
            'Travail d\xc3\xa9cent et croissance \xc3\xa9conomique']
        self.form.getControl(name=self.observation_input_name).value = 'Constat'
        self.form.getControl(name=self.comments_input_name).value = 'Commentaires'
        self.form.submit(name=self.save_input_name)

    def step_5a(self):
        """The user clicks on the "! Cancel" button."""
        self.form.submit(name=self.cancel_input_name)

    def step_5b(self):
        """The user does not fill in required fields and save."""
        self.form.submit(name=self.save_input_name)

    def step_6(self):
        """The system creates and displays the element."""
        self.assertEqual(self.browser.title, 'Titre (OO.24) \xe2\x80\x94 Site')

    def step_6a(self):
        """The system return to the previous page without save"""
        self.assertTrue("Ajout annul\xc3\xa9" in self.browser.contents)

    def step_6b(self):
        """
        The system displays warnings
        pre-populates and displays the form for editing an operational objective.
        """
        self.assertTrue("Il y a des erreurs" in self.browser.contents)
