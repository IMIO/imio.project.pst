# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase


def step_3_a1(browser):
    """The user cancel the form."""
    form = browser.forms['form']
    form.find_button_by_label('Annuler').click()


class TestUpdatePstAction(FunctionalTestCase):
    """Test use case.
    Name: Update pstaction
    Actor(s): pst_editors, actioneditor
    Description: The updating of an action must be possible for a global editor,
                 an action manager as well as an administrator
    Author: Franck Ngaha
    Created: 03/12/2020
    Preconditions: The user must be authenticated as a global editor or action manager or administrator
    Start: The user is on the page of an action
    """

    def setUp(self):
        super(TestUpdatePstAction, self).setUp()
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_10 = self.pst[
            'etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-de-serre-afin-dassu'
            'rer-le-developpement-durable']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']
        self.a_16 = self.oo_15['reduire-la-consommation-energetique-de-ladministration-communale']

    @browsing
    def test_nominal_scenario(self, browser):
        self.preconditions(browser)  # Login as psteditor
        self.start_up(browser)  # Open (A.16)
        self.step_1(browser)  # The user opens edit form
        self.step_2(browser)  # The system displays action's edit form
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
        (2020, 10, 29) < (2020, 10, 31)
        """
        self.preconditions(browser)
        self.start_up(browser)
        self.step_1(browser)
        self.step_2(browser)
        self.step_3_a3(browser)  # The user fills a smaller planned end date
        self.step_4_a3(browser)  # The system updates element with warning message

    @browsing
    def test_alternative_a4(self, browser):
        """
        The user fills a planned end date larger than their operational objective.
        (2025, 12, 31) < (2024, 12, 31)
        """
        self.preconditions(browser)
        self.start_up(browser)
        self.step_1(browser)
        self.step_2(browser)
        self.step_3_a4(browser)  # The user fills a larger planned end date
        self.step_4_a4(browser)  # The system updates element with warning message

    def preconditions(self, browser):
        """Login as psteditor."""
        browser.login(username='psteditor', password=self.password).open()

    def start_up(self, browser):
        """Open (A.16)."""
        browser.open(self.a_16)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u"Réduire la consommation énergétique de l'administration communale (A.16)", heading.text)

    def step_1(self, browser):
        """The user opens edit form."""
        browser.open(self.a_16.absolute_url() + '/edit')

    def step_2(self, browser):
        """The system displays action's edit form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(u'Editer Action', heading.text)

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
        fields[self.planned_end_date_day_form_widget_name] = u'29'
        fields[self.planned_end_date_month_form_widget_name] = u'10'
        fields[self.planned_end_date_year_form_widget_name] = u'2020'
        form.find_button_by_label('Sauvegarder').click()

    def step_3_a4(self, browser):
        """The user fills a larger planned end date."""
        form = browser.forms['form']
        fields = form.values
        fields[self.planned_end_date_day_form_widget_name] = u'31'
        fields[self.planned_end_date_month_form_widget_name] = u'12'
        fields[self.planned_end_date_year_form_widget_name] = u'2025'
        form.find_button_by_label('Sauvegarder').click()

    def step_4(self, browser):
        """The system save changes with "Modify changes" info success."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual('Titre (A.16)', heading.text)
        statusmessages.assert_message(u'Modifications sauvegardées')

    def step_4_a1(self, browser):
        """The system back to the previous page with 'Modification canceled' Info."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(
            u"Réduire la consommation énergétique de l'administration communale (A.16)",
            heading.text)
        statusmessages.assert_message(u'Modification annulée')

    def step_4_a2(self, browser):
        """The system displays the max planned end date of the contained items with a warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(
            u"Réduire la consommation énergétique de l'administration communale (A.16)",
            heading.text
        )
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance n'est pas encodée sur l'action, "
             u"le système affiche celle la plus grande de ses éventuelles sous-actions"]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['31/10/2020'])

    def step_4_a3(self, browser):
        """The system updates element with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(
            u"Réduire la consommation énergétique de l'administration communale (A.16)",
            heading.text
        )
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance d'au moins une sous action est supérieure à celle de l'action"]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['29/10/2020'])

    def step_4_a4(self, browser):
        """The system updates element with warning message."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual(
            u"Réduire la consommation énergétique de l'administration communale (A.16)",
            heading.text
        )
        self.assertEqual(
            browser.css('#messagesviewlet').text,
            [u"Avertissement La date d'échéance de l'action est supérieure à celle de l'objcectif opérationnel"]
        )
        statusmessages.assert_message(u'Modifications sauvegardées')
        self.assertEqual(browser.css('#form-widgets-planned_end_date').text, ['31/12/2025'])
