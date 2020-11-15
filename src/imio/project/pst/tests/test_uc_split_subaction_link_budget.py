# -*- coding: utf-8 -*-
from ftw.testbrowser.pages import statusmessages
from imio.project.pst.testing import FunctionalTestCase
from ftw.testbrowser import browsing


def step_4b():
    """The system displays warnings."""
    statusmessages.assert_message('Il y a des erreurs.')


def step_3a(browser):
    """The user clicks on the "! Cancel" button."""
    browser.find_button_by_label('Retour').click()


class TestSplitSubActionLinkBudget(FunctionalTestCase):
    """
    Name: Split sub action link budget
    Actor(s): admin, pst_editors, actioneditor
    Description: The distribution of budgets must be possible for a global editor, an action manager as well as an administrator
    Author: Franck Ngaha
    Date: 12/11/2020
    Preconditions: The user must be authenticated as a global editor or actioneditor or administrator
    Start: The user is on a sub action link page
    """

    def setUp(self):
        super(TestSplitSubActionLinkBudget, self).setUp()
        self.portal = self.layer['portal']
        self.pst = self.portal['pst']
        self.os_10 = self.pst['etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-d'
                              'e-serre-afin-dassurer-le-developpement-durable']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']
        self.a_20 = self.oo_15['reduire-la-consommation-energetique-du-hangar-communal']
        self.sa_l_17 = self.a_20['realiser-un-audit-energetique-du-batiment']
        self.a_16 = self.oo_15['reduire-la-consommation-energetique-de-ladministration-communale']
        self.sa_17 = self.a_20['realiser-un-audit-energetique-du-batiment']

    @browsing
    def test_scenario(self, browser):
        # The user must be authenticated as pst_editors or actioneditor or admin
        # Login as pst_editors
        self.preconditions(browser)
        # The user is on the sub action link page
        # Visit (SA.17)
        self.start_up(browser)
        # The user clicks on the link "Split budget lines between multiple instances"
        self.step_1(browser)
        # The system displays the form
        self.step_2(browser)
        # The user encodes the "Percentage" fields and clicks save
        self.step_3(browser)
        # The system updates the values of the fields of the different hierarchies
        self.step_4(browser)

    @browsing
    def test_alternative_3a(self, browser):
        # The user must be authenticated as pst_editors or actioneditor or admin
        # Login as pst_editors
        self.preconditions(browser)
        # The user is on the sub action link page
        # Visit (SA.17)
        self.start_up(browser)
        # The user clicks on the link "Split budget lines between multiple instances"
        self.step_1(browser)
        # The system displays the form
        self.step_2(browser)
        # The user clicks on the "! Cancel" button
        step_3a(browser)
        # The system return to the previous page without save
        self.step_4a(browser)

    @browsing
    def test_exceptional_ba(self, browser):
        # The user must be authenticated as pst_editors or actioneditor or admin
        # Login as pst_editors
        self.preconditions(browser)
        # The user is on the sub action link page
        # Visit (SA.17)
        self.start_up(browser)
        # The user clicks on the link "Split budget lines between multiple instances"
        self.step_1(browser)
        # The system displays the form
        self.step_2(browser)
        # The user encodes the fields incorrectly and save
        self.step_3b(browser)
        # The system displays warnings
        step_4b()

    def preconditions(self, browser):
        """Login as pst_editors."""
        browser.login(username='psteditor', password=self.password).open()

    def start_up(self, browser):
        """Open (SA.17)."""
        browser.open(self.sa_l_17)
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual("Réaliser un audit énergétique du bâtiment (SA.17)".decode('utf8'), heading.text)

    def step_1(self, browser):
        """The user clicks on the link "Split budget lines between multiple instances"."""
        browser.click_on("Répartir les lignes budgétaires entre les différentes actions".decode('utf8'))

    def step_2(self, browser):
        """The system displays the form."""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual("Répartition des budgets entre les différentes actions".decode('utf8'), heading.text)

    def step_3(self, browser):
        """The user encodes the "Percentage" fields and clicks save."""
        self.assertEqual(browser.css('#form-widgets-budget_split-0-widgets-percentage').first.value, '100,0')
        self.assertEqual(browser.css('#form-widgets-budget_split-1-widgets-percentage').first.value, '0,0')
        browser.fill({'form.widgets.budget_split.0.widgets.percentage': "50,0",
                      'form.widgets.budget_split.1.widgets.percentage': "50,0"}).submit()

    def step_4(self, browser):
        """The system updates the values of the fields of the different hierarchies."""
        # <<<<<<<
        # {'': 'Wallonie', 'Global': '-', '2024': '-', '2020': '-', '2021': '-', '2022': '-', '2023': '-', '2019': '-'}
        # =======
        # {'': 'Wallonie', 'Global': '1000.0', '2024': '-', '2020': '250.0', '2021': '250.0', '2022': '250.0',
        # '2023': '-', '2019': '250.0'}
        # >>>>>>>
        browser.open(self.a_20)
        self.assertEqual(browser.css('.budgetinfos_table').first.dicts(), [
            {'': 'Europe', 'Global': '0.0', '2024': '-', '2020': '-', '2021': '0.0', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': 'Province', 'Global': '-', '2024': '-', '2020': '-', '2021': '-', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': 'Ville', 'Global': '-', '2024': '-', '2020': '-', '2021': '-', '2022': '-', '2023': '-', '2019': '-'},
            {'': u'F\xe9d\xe9ral', 'Global': '0.0', '2024': '-', '2020': '-', '2021': '0.0', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': 'Wallonie', 'Global': '1000.0', '2024': '-', '2020': '250.0', '2021': '250.0', '2022': '250.0',
             '2023': '-', '2019': '250.0'},
            {'': 'Autres', 'Global': '0.0', '2024': '-', '2020': '-', '2021': '0.0', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': u'F\xe9d\xe9ration Wallonie-Bruxelles', 'Global': '-', '2024': '-', '2020': '-', '2021': '-',
             '2022': '-', '2023': '-', '2019': '-'},
            {'': 'Totaux', 'Global': '1000.0', '2024': '-', '2020': '250.0', '2021': '250.0', '2022': '250.0',
             '2023': '-', '2019': '250.0'}])
        # <<<<<<<
        # {'': 'Wallonie', 'Global': '6500.0', '2024': '-', '2020': '1500.0', '2021': '2000.0', '2022': '1500.0',
        # '2023': '-', '2019': '1500.0'}
        # =======
        # {'': 'Wallonie', 'Global': '5500.0', '2024': '-', '2020': '1250.0', '2021': '1750.0', '2022': '1250.0',
        # '2023': '-', '2019': '1250.0'}
        # >>>>>>>
        browser.open(self.a_16)
        self.assertEqual(browser.css('.budgetinfos_table').first.dicts(), [
            {'': 'Europe', 'Global': '500.0', '2024': '-', '2020': '-', '2021': '500.0', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': 'Province', 'Global': '-', '2024': '-', '2020': '-', '2021': '-', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': 'Ville', 'Global': '-', '2024': '-', '2020': '-', '2021': '-', '2022': '-', '2023': '-', '2019': '-'},
            {'': u'F\xe9d\xe9ral', 'Global': '500.0', '2024': '-', '2020': '-', '2021': '500.0', '2022': '-',
             '2023': '-', '2019': '-'},
            {'': 'Wallonie', 'Global': '5500.0', '2024': '-', '2020': '1250.0', '2021': '1750.0', '2022': '1250.0',
             '2023': '-', '2019': '1250.0'},
            {'': 'Autres', 'Global': '500.0', '2024': '-', '2020': '-', '2021': '500.0', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': u'F\xe9d\xe9ration Wallonie-Bruxelles', 'Global': '-', '2024': '-', '2020': '-', '2021': '-',
             '2022': '-', '2023': '-', '2019': '-'},
            {'': 'Totaux', 'Global': '7000.0', '2024': '-', '2020': '1250.0', '2021': '3250.0', '2022': '1250.0',
             '2023': '-', '2019': '1250.0'}])
        browser.open(self.oo_15)
        self.assertEqual(browser.css('.budgetinfos_table').first.dicts(), [
            {'': 'Europe', 'Global': '500.0', '2024': '-', '2020': '-', '2021': '500.0', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': 'Province', 'Global': '-', '2024': '-', '2020': '-', '2021': '-', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': 'Ville', 'Global': '-', '2024': '-', '2020': '-', '2021': '-', '2022': '-', '2023': '-', '2019': '-'},
            {'': u'F\xe9d\xe9ral', 'Global': '500.0', '2024': '-', '2020': '-', '2021': '500.0', '2022': '-',
             '2023': '-', '2019': '-'},
            {'': 'Wallonie', 'Global': '6500.0', '2024': '-', '2020': '1500.0', '2021': '2000.0', '2022': '1500.0',
             '2023': '-', '2019': '1500.0'},
            {'': 'Autres', 'Global': '500.0', '2024': '-', '2020': '-', '2021': '500.0', '2022': '-', '2023': '-',
             '2019': '-'},
            {'': u'F\xe9d\xe9ration Wallonie-Bruxelles', 'Global': '-', '2024': '-', '2020': '-', '2021': '-',
             '2022': '-', '2023': '-', '2019': '-'},
            {'': 'Totaux', 'Global': '8000.0', '2024': '-', '2020': '1500.0', '2021': '3500.0', '2022': '1500.0',
             '2023': '-', '2019': '1500.0'}])

    def step_4a(self, browser):
        """The system return to the previous page without save"""
        heading = browser.css('.documentFirstHeading').first
        self.assertEqual("Réaliser un audit énergétique du bâtiment (SA.17)".decode('utf8'), heading.text)

    def step_3b(self, browser):
        """The user encodes the fields incorrectly and save."""
        self.assertEqual(browser.css('#form-widgets-budget_split-0-widgets-percentage').first.value, '100,0')
        self.assertEqual(browser.css('#form-widgets-budget_split-1-widgets-percentage').first.value, '0,0')
        browser.fill({
            'form.widgets.budget_split.0.widgets.percentage': "75,0",
            'form.widgets.budget_split.1.widgets.percentage': "75,0"
        }).submit()
