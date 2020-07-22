# -*- coding: utf-8 -*-
""" pstprojectspace.py tests for this package."""

from imio.project.pst.testing import IntegrationTestCase
from zope.event import notify
from zope.interface import Interface
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import ObjectModifiedEvent


class TestPSTProjectSpace(IntegrationTestCase):
    """Test pstprojectspace.py."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestPSTProjectSpace, self).setUp()

    def test_default_setup(self):
        """
         Assert that pstprojectspace has default fields values
        """
        self.assertEquals(self.pst.strategicobjective_fields, self.os_fields)
        self.assertEquals(self.pst.operationalobjective_fields, self.oo_fields)
        self.assertEquals(self.pst.pstaction_fields, self.a_fields)
        self.assertEquals(self.pst.pstsubaction_fields, self.a_fields)
        self.assertEquals(self.pst.strategicobjectives_columns, self.os_columns)
        self.assertEquals(self.pst.operationalobjectives_columns, self.oo_columns)
        self.assertEquals(self.pst.pstactions_columns, self.a_columns)
        self.assertEquals(self.pst.strategicobjective_budget_states, self.so_bdg_states)
        self.assertEquals(self.pst.operationalobjective_budget_states, self.oo_bdg_states)
        self.assertEquals(self.pst.pstaction_budget_states, self.a_bdg_states)
        self.assertEquals(self.pst.pstsubaction_budget_states, self.a_bdg_states)

    def test_strategicobjectives_fields(self):
        """
         Test hide field :
         remove categories in strategicobjectives_fields and assert that schemata fields has been updated
        """
        self.assertEquals(
            self.pst.strategicobjective_fields,
            ['IDublinCore.title', 'description_rich', 'reference_number', 'categories', 'plan',
             'IAnalyticBudget.projection', 'IAnalyticBudget.analytic_budget', 'budget', 'budget_comments',
             'observation', 'comments']
        )
        self.pst.strategicobjective_fields.remove('categories')
        self.assertEquals(
            self.pst.strategicobjective_fields,
            ['IDublinCore.title', 'description_rich', 'reference_number', 'plan', 'IAnalyticBudget.projection',
             'IAnalyticBudget.analytic_budget', 'budget', 'budget_comments', 'observation', 'comments']
        )
        os_view = self.os1.unrestrictedTraverse('@@view')
        os_view.updateFieldsFromSchemata()
        schema_fields = [fld for fld in os_view.fields]
        self.assertEquals(
            schema_fields,
            ['description_rich', 'reference_number', 'plan', 'IAnalyticBudget.projection',
             'IAnalyticBudget.analytic_budget', 'budget', 'budget_comments', 'observation', 'comments']
        )

    def test_pstsubaction_fields(self):
        """
         Test value when pstaction_fields modified :
         remove plan in pstaction_fields and assert that pstsubaction_fields take same values
        """
        self.assertEquals(self.pst.pstsubaction_fields, self.pst.pstaction_fields)
        # remove 'plan' value
        self.pst.pstaction_fields = ['IDublinCore.title', 'description_rich', 'reference_number', 'categories',
                                     'result_indicator', 'planned_end_date', 'planned_begin_date',
                                     'effective_begin_date', 'effective_end_date',
                                     'progress', 'health_indicator', 'health_indicator_details',
                                     'representative_responsible', 'manager',
                                     'responsible', 'extra_concerned_people', 'IAnalyticBudget.projection',
                                     'IAnalyticBudget.analytic_budget',
                                     'budget', 'budget_comments', 'ISustainableDevelopmentGoals.sdgs', 'observation',
                                     'comments']
        self.assertNotEquals(self.pst.pstsubaction_fields, self.pst.pstaction_fields)
        notify(ObjectModifiedEvent(self.pst, Attributes(Interface, 'pstaction_fields')))
        self.assertEquals(self.pst.pstsubaction_fields, self.pst.pstaction_fields)

    def test_strategicobjectives_columns(self):
        """
        Test dashboard columns config :
        remove select_row in strategicobjectives_columns and assert that dashboard config has been adapted
        """
        # Test dashboard columns config
        self.assertEquals(
            self.pst.strategicobjectives_columns,
            [u'select_row', u'pretty_link', u'review_state', u'categories', u'ModificationDate', u'history_actions']
        )
        self.pst.strategicobjectives_columns.remove('select_row')
        self.assertEquals(
            self.pst.strategicobjectives_columns,
            [u'pretty_link', u'review_state', u'categories', u'ModificationDate', u'history_actions']
        )
        self.assertEquals(
            self.pst.strategicobjectives.all.customViewFields,
            (u'select_row', u'pretty_link', u'review_state', u'categories', u'ModificationDate', u'history_actions')
        )
        notify(ObjectModifiedEvent(self.pst, Attributes(Interface, 'strategicobjectives_columns')))
        self.assertEquals(
            self.pst.strategicobjectives.all.customViewFields,
            (u'pretty_link', u'review_state', u'categories', u'ModificationDate', u'history_actions')
        )

    def test_pstsubaction_budget_states(self):
        """
         Test value when pstaction_budget_states modified :
         remove 'to_be_scheduled' in pstaction_budget_states and assert that pstsubaction_budget_states take same values
        """
        self.login('psteditor')
        self.assertEquals(self.pst.pstsubaction_budget_states, self.pst.pstaction_budget_states)
        # remove 'to_be_scheduled' value in pstaction_budget_states = ['ongoing', 'terminated', 'to_be_scheduled']
        self.pst.pstaction_budget_states = ['ongoing', 'terminated']
        self.assertNotEquals(self.pst.pstsubaction_budget_states, self.pst.pstaction_budget_states)
        notify(ObjectModifiedEvent(self.pst, Attributes(Interface, 'pstaction_budget_states')))
        self.assertEquals(self.pst.pstsubaction_budget_states, self.pst.pstaction_budget_states)
