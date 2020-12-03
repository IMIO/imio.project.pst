# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase


def step_3_a1(browser):
    """The user cancel the form."""
    form = browser.forms['form']
    form.find_button_by_label('Annuler').click()


class TestUpdateOperationalObjective(FunctionalTestCase):
    """Test use case.
    Name: Update an operational objective
    Actor(s): pst_editors, admin_resp
    Description: The updating of an operational objective must be possible for a global editor,
                 an administrative manager as well as an administrator
    Author: Franck Ngaha
    Created: 25/11/2020
    Updated: 03/12/2020
    Preconditions: The user must be authenticated as a global editor or administrative manager or administrator
    Start: The user is on the page of a operational objective
    """

    def setUp(self):
        super(TestUpdateOperationalObjective, self).setUp()
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_10 = self.pst[
            'etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-de-serre-afin-dassu'
            'rer-le-developpement-durable']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']

    @browsing
    def test_nominal_scenario(self, browser):
        self.preconditions(browser)  # Login as psteditor
        self.start_up(browser)  # Open (OO.15)
        self.step_1(browser)  # The user opens edit form
        self.step_2(browser)  # The system displays operational objective's edit form
        self.step_3(browser)  # The user update title and save
        self.step_4(browser)  # The system save changes with "Modify changes" info success

    @browsing
    def test_alternative_a1(self, browser):
        """The user cancel the form."""
        self.preconditions(browser)
        self.start_up(browser)
        self.step_1(browser)
        self.step_2(browser)
        step_3_a1(browser)  # The user cancel the form
        self.step_4_a1(browser)  # The system back to the previous page with "Addition canceled" Info

    @browsing
    def test_alternative_a2(self, browser):
        """The user remove the deadline and save."""
        self.preconditions(browser)
        self.start_up(browser)
        self.step_1(browser)
        self.step_2(browser)
        self.step_3_a2(browser)  # The user removes the deadline
        self.step_4_a2(browser)  # The system displays the max planned end date of the contained items and warn

    @browsing
    def test_alternative_a3(self, browser):
        """
        The user fills a planned end date smaller than the largest of their contained actions.
        (2023, 06, 30) < (2024, 06, 30)
        """
        self.preconditions(browser)
        self.start_up(browser)
        self.step_1(browser)
        self.step_2(browser)
        self.step_3_a3(browser)  # The user fills a smaller planned end date
        self.step_4_a3(browser)  # The system updates element with warning message

    def preconditions(self, browser):
        """Login as psteditor."""
        browser.login(username='psteditor', password=self.password).open()

    def start_up(self, browser):
        """Open (OO.15)."""
        browser.open(self.oo_15)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u"Réduire la consommation énergétique des bâtiments communaux de 20% d'ici 2024 (OO.15)",
                         heading.text)

    def step_1(self, browser):
        """The user opens edit form."""
        browser.open(self.oo_15.absolute_url() + '/edit')

    def step_2(self, browser):
        """The system displays operational objective's edit form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Editer Objectif opérationnel', heading.text)

    def step_3(self, browser):
        """The user update title and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.title_form_widget_name] = u'Titre'
        form.find_button_by_label('Sauvegarder').click()

    def step_3_a2(self, browser):
        """The user remove the deadline and save."""
        form = browser.forms['form']
        fields = form.values
        fields[self.planned_end_date_day_form_widget_name] = u''
        fields[self.planned_end_date_month_form_widget_name] = u''
        fields[self.planned_end_date_year_form_widget_name] = u''
        form.find_button_by_label('Sauvegarder').click()

    def step_3_a3(self, browser):
        """The user fills a smaller planned end date."""
        form = browser.forms['form']
        fields = form.values
        fields[self.planned_end_date_day_form_widget_name] = u'30'
        fields[self.planned_end_date_month_form_widget_name] = u'6'
        fields[self.planned_end_date_year_form_widget_name] = u'2023'
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser):
        """The system save changes with "Modify changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (OO.15)', heading.text)
        statusmessages.assert_message(u'Modifications sauvegardées')

    def step_4_a1(self, browser):
        """The system back to the previous page with 'Modification canceled' Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(
            u"Réduire la consommation énergétique des bâtiments communaux de 20% d'ici 2024 (OO.15)",
            heading.text)
        statusmessages.assert_message(u'Modification annulée')

    def step_4_a2(self, browser):
        """The system displays the max planned end date of the contained items with a warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(
            u"Réduire la consommation énergétique des bâtiments communaux de 20% d'ici 2024 (OO.15)",
            heading.text
        )
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance n'est pas encodée sur l'obectif opérationnel, "
             u"le système affiche celle la plus grande de ses éventuelles actions"]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['30/06/2024'])

    def step_4_a3(self, browser):
        """The system updates element with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(
            u"Réduire la consommation énergétique des bâtiments communaux de 20% d'ici 2024 (OO.15)",
            heading.text
        )
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance d'au moins une action est supérieure à celle de l'objectif "
             u"opérationnel"]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['30/06/2023'])
