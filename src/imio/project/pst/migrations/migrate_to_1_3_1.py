# -*- coding: utf-8 -*-

from imio.migrator.migrator import Migrator
from plone import api

import logging


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_3_1(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):

        # update registry fields settings with plan key
        api.portal.set_registry_record(
                'imio.project.settings.strategicobjective_fields',
                [
                    'IDublinCore.title', 'description_rich', 'reference_number', 'categories',
                    'IAnalyticBudget.projection', 'IAnalyticBudget.analytic_budget', 'budget',
                    'budget_comments', 'observation', 'comments', 'plan'
                ]
        )
        api.portal.set_registry_record(
                'imio.project.settings.operationalobjective_fields',
                [
                    'IDublinCore.title', 'description_rich', 'reference_number', 'categories',
                    'result_indicator', 'priority', 'planned_end_date', 'representative_responsible',
                    'administrative_responsible', 'manager', 'extra_concerned_people',
                    'IAnalyticBudget.projection', 'IAnalyticBudget.analytic_budget', 'budget',
                    'budget_comments', 'ISustainableDevelopmentGoals.sdgs', 'observation', 'comments', 'plan'
                ]
        )
        api.portal.set_registry_record(
                'imio.project.settings.pstaction_fields',
                [
                    'IDublinCore.title', 'description_rich', 'reference_number', 'categories',
                    'result_indicator', 'planned_end_date', 'planned_begin_date', 'effective_begin_date',
                    'effective_end_date', 'progress', 'health_indicator', 'health_indicator_details',
                    'representative_responsible', 'manager', 'responsible', 'extra_concerned_people',
                    'IAnalyticBudget.projection', 'IAnalyticBudget.analytic_budget', 'budget',
                    'budget_comments', 'ISustainableDevelopmentGoals.sdgs', 'observation', 'comments', 'plan'
                ]
        )
        api.portal.set_registry_record(
                'imio.project.settings.pstsubaction_fields',
                api.portal.get_registry_record('imio.project.settings.pstaction_fields')
        )

        # add plan values to project space
        plan_values = [
            {'label': u"Agenda 21 local", 'key': "agenda-21-local"},
            {'label': u"PCA Plan communal d'Aménagement", 'key': "pca-plan-communal-d-amenagement"},
            {'label': u"Plan communal d'Urgence", 'key': "plan-communal-d-urgence"},
            {'label': u"Plan communal de développement de la nature PCDN", 'key': "plan-communal-de-developpement-de-la-nature-pcdn"},
            {'label': u"Plan communal de développement rural (PCDR)", 'key': "plan-communal-de-developpement-rural-pcdn"},
            {'label': u"Plan d'ancrage communal", 'key': "plan-d-ancrage-communal"},
            {'label': u"Plan de cohésion social (PCS)", 'key': "plan-de-cohesion-social-pcs"},
            {'label': u"Plan de formation du personnel", 'key': "plan-de-formation-du-personnel"},
            {'label': u"Plan de gestion", 'key': "plan-de-gestion"},
            {'label': u"Plan de mobilité", 'key': "plan-de-mobilite"},
            {'label': u"Plan global de prévention", 'key': "plan-global-de-prevention"},
            {'label': u"Plan zonal de sécurité", 'key': "plan-zonal-de-securite"},
            {'label': u"Schémas de développement commercial", 'key': "schemas-de-developpement-commercial"},
        ]
        site = api.portal.getSite()
        projectspace = site.pst
        projectspace.plan_values = plan_values

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_1_3_1(context).run()
