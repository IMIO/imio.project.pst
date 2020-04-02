# -*- coding: utf-8 -*-

from imio.migrator.migrator import Migrator
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import logging


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_3_1(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def add_plan_to_registry_record(self, record_name):
        registry = getUtility(IRegistry)
        if 'plan' not in registry[record_name]:
            if 'categories' in registry[record_name]:
                registry[record_name].insert(
                        registry[record_name].index('categories') + 1, 'plan')
            else:
                registry[record_name].append('plan')

    def run(self):

        # update registry imio project settings with plan field
        registry = getUtility(IRegistry)

        so_rn = 'imio.project.settings.strategicobjective_fields'
        if not registry.get(so_rn):
            registry[so_rn] = [
                'IDublinCore.title', 'description_rich', 'reference_number',
                'categories', 'plan', 'IAnalyticBudget.projection',
                'IAnalyticBudget.analytic_budget', 'budget', 'budget_comments',
                'observation', 'comments']
        else:
            self.add_plan_to_registry_record(so_rn)
        oo_rn = 'imio.project.settings.operationalobjective_fields'
        if not registry.get(oo_rn):
            registry[oo_rn] = [
                'IDublinCore.title', 'description_rich', 'reference_number',
                'categories', 'plan', 'result_indicator', 'priority',
                'planned_end_date', 'representative_responsible',
                'administrative_responsible', 'manager',
                'extra_concerned_people', 'IAnalyticBudget.projection',
                'IAnalyticBudget.analytic_budget', 'budget', 'budget_comments',
                'ISustainableDevelopmentGoals.sdgs', 'observation', 'comments']
        else:
            self.add_plan_to_registry_record(oo_rn)
        act_rn = 'imio.project.settings.pstaction_fields'
        if not registry.get(act_rn):
            registry[act_rn] = [
                'IDublinCore.title', 'description_rich', 'reference_number',
                'categories', 'plan', 'result_indicator', 'planned_end_date',
                'planned_begin_date', 'effective_begin_date',
                'effective_end_date', 'progress', 'health_indicator',
                'health_indicator_details', 'representative_responsible',
                'manager', 'responsible', 'extra_concerned_people',
                'IAnalyticBudget.projection',
                'IAnalyticBudget.analytic_budget', 'budget', 'budget_comments',
                'ISustainableDevelopmentGoals.sdgs', 'observation', 'comments']
        else:
            self.add_plan_to_registry_record(act_rn)
        sact_rn = 'imio.project.settings.pstsubaction_fields'
        if not registry.get(sact_rn):
            registry[sact_rn] = registry[act_rn]
        else:
            self.add_plan_to_registry_record(sact_rn)

        # add plan values to project space
        plan_values = [
            {'label': u"Agenda 21 local",
                'key': "agenda-21-local"},
            {'label': u"PCA Plan communal d'Aménagement",
                'key': "pca-plan-communal-d-amenagement"},
            {'label': u"Plan communal d'Urgence",
                'key': "plan-communal-d-urgence"},
            {'label': u"Plan communal de développement de la nature PCDN",
                'key': "plan-communal-de-developpement-de-la-nature-pcdn"},
            {'label': u"Plan communal de développement rural (PCDR)",
                'key': "plan-communal-de-developpement-rural-pcdn"},
            {'label': u"Plan d'ancrage communal",
                'key': "plan-d-ancrage-communal"},
            {'label': u"Plan de cohésion social (PCS)",
                'key': "plan-de-cohesion-social-pcs"},
            {'label': u"Plan de formation du personnel",
                'key': "plan-de-formation-du-personnel"},
            {'label': u"Plan de gestion",
                'key': "plan-de-gestion"},
            {'label': u"Plan de mobilité",
                'key': "plan-de-mobilite"},
            {'label': u"Plan global de prévention",
                'key': "plan-global-de-prevention"},
            {'label': u"Plan zonal de sécurité",
                'key': "plan-zonal-de-securite"},
            {'label': u"Schémas de développement commercial",
                'key': "schemas-de-developpement-commercial"},
        ]
        brains=self.catalog(object_provides='imio.project.pst.interfaces.IImioPSTProject')
        for brain in brains:
            project = brain.getObject()
            if not project.plan_values:
                project.plan_values = plan_values

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_1_3_1(context).run()
