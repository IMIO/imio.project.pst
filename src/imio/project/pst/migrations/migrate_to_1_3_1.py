# -*- coding: utf-8 -*-

from imio.migrator.migrator import Migrator
from imio.project.core.content.projectspace import IProjectSpace
from plone import api
from plone.app.contenttypes.migration.dxmigration import migrate_base_class_to_new_class
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import logging


logger = logging.getLogger('imio.project.pst')


class Migrate_To_1_3_1(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def add_plan_to_lists_fields(self, *lists_fields):
        for list_fields in lists_fields:
            if 'plan' not in list_fields:
                if 'categories' in list_fields:
                    list_fields.insert(list_fields.index('categories') + 1, 'plan')
                else:
                    list_fields.append('plan')

    def run(self):

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

        registry = getUtility(IRegistry)
        so_record = registry.get('imio.project.settings.strategicobjective_fields')
        oo_record = registry.get('imio.project.settings.operationalobjective_fields')
        act_record = registry.get('imio.project.settings.pstaction_fields')
        if so_record and oo_record and act_record:
            self.add_plan_to_lists_fields(so_record, oo_record, act_record)
            self.runProfileSteps('imio.project.pst', steps=['typeinfo'], profile='default',
                    run_dependencies=False)
            projectspace_brains = self.catalog(object_provides=IProjectSpace.__identifier__)
            if projectspace_brains[0].getObject().__class__.__name__ == 'ProjectSpace':
                for projectspace_brain in projectspace_brains:
                    projectspace_obj = projectspace_brain.getObject()
                    migrate_base_class_to_new_class(
                            projectspace_obj,
                            new_class_name='imio.project.pst.content.pstprojectspace.PSTProjectSpace')
                    #projectspace is now pstprojectspace
                    projectspace_obj.portal_type = 'pstprojectspace'
                    projectspace_obj.strategicobjective_fields = so_record
                    projectspace_obj.operationalobjective_fields = oo_record
                    projectspace_obj.pstaction_fields = act_record
                    projectspace_obj.pstsubaction_fields = act_record
                    if not hasattr(projectspace_obj, 'plan_values'):
                        setattr(projectspace_obj, 'plan_values', plan_values)

                del registry.records['imio.project.settings.strategicobjective_fields']
                del registry.records['imio.project.settings.operationalobjective_fields']
                del registry.records['imio.project.settings.pstaction_fields']

        # Display duration
        self.finish()


def migrate(context):
    Migrate_To_1_3_1(context).run()
