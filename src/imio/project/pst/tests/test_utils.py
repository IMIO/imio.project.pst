# -*- coding: utf-8 -*-
""" Content action tests for this package."""
from datetime import datetime

from imio.project.pst.testing import IntegrationTestCase
from imio.project.pst.utils import find_deadlines_on_children, find_max_deadline_on_children, find_brains_on_parents, \
    find_deadlines_on_parents, is_smaller_deadline_on_parents


class TestUtils(IntegrationTestCase):
    """Test action.py."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestUtils, self).setUp()
        self.os_10 = self.pst['etre-une-commune-qui-sinscrit-dans-la-lignee-des-accords-de-reductions-des-gaz-a-effet-'
                              'de-serre-afin-dassurer-le-developpement-durable']
        self.oo_15 = self.os_10['reduire-la-consommation-energetique-des-batiments-communaux-de-20-dici-2024']
        self.a_16 = self.oo_15['reduire-la-consommation-energetique-de-ladministration-communale']
        self.sa_17 = self.a_16['realiser-un-audit-energetique-du-batiment']
        self.task = self.sa_17['ecrire-le-cahier-des-charges']

    def test_find_deadlines_on_operational_objective_children(self):
        """Test find_deadlines_on_operational_objective_children method on operational objective."""
        self.assertEqual(
            find_deadlines_on_children(
                self.oo_15,
                {
                    "pstaction": "planned_end_date",
                    "pstsubaction": "planned_end_date",
                    "subaction_link": "planned_end_date",
                    "task": "due_date"
                }
            ),
            [
                datetime.date(datetime(2024, 6, 30)),
                datetime.date(datetime(2020, 6, 30)),
                datetime.date(datetime(2020, 4, 30)),
                datetime.date(datetime(2020, 3, 31)),
                datetime.date(datetime(2020, 10, 31)),
                datetime.date(datetime(2020, 10, 31)),
                datetime.date(datetime(2024, 6, 30)),
                datetime.date(datetime(2020, 4, 30)),
                datetime.date(datetime(2020, 3, 31)),
                datetime.date(datetime(2020, 6, 30)),
                datetime.date(datetime(2020, 10, 31)),
                datetime.date(datetime(2020, 10, 31)),
            ]
        )

    def test_find_deadlines_on_pst_action_children(self):
        """Test find_deadlines_on_pst_action_children method on pst action."""
        self.assertEqual(
            find_deadlines_on_children(
                self.a_16,
                {
                    "pstsubaction": "planned_end_date",
                    "subaction_link": "planned_end_date",
                    "task": "due_date"
                }
            ),
            [
                datetime.date(datetime(2020, 6, 30)),
                datetime.date(datetime(2020, 4, 30)),
                datetime.date(datetime(2020, 3, 31)),
                datetime.date(datetime(2020, 10, 31)),
                datetime.date(datetime(2020, 10, 31))
            ]
        )

    def test_find_deadlines_on_pst_sub_action_children(self):
        """Test find_deadlines_on_pst_sub_action_children method on pst sub action."""
        self.assertEqual(
            find_deadlines_on_children(self.sa_17, {"task": "due_date"}),
            [datetime.date(datetime(2020, 4, 30)), datetime.date(datetime(2020, 3, 31))]
        )

    def test_find_max_deadline_on_operational_objective_children(self):
        """Test find_max_deadline_on_operational_objective_children method on operational objective."""
        self.assertEqual(
            find_max_deadline_on_children(
                self.oo_15,
                {
                    "pstsubaction": "planned_end_date",
                    "subaction_link": "planned_end_date",
                    "task": "due_date"
                }
            ),
            datetime.date(datetime(2020, 10, 31))
        )

    def test_find_max_deadline_on_pst_action_children(self):
        """Test find_max_deadline_on_pst_action_children method on pst action."""
        self.assertEqual(
            find_max_deadline_on_children(
                self.a_16,
                {
                    "pstsubaction": "planned_end_date",
                    "subaction_link": "planned_end_date",
                    "task": "due_date"
                }
            ),
            datetime.date(datetime(2020, 10, 31))
        )

    def test_find_max_deadline_on_pst_sub_action_children(self):
        """Test find_max_deadline_on_pst_sub_action_children method on pst sub action."""
        self.assertEqual(
            find_max_deadline_on_children(self.sa_17, {"task": "due_date"}),
            datetime.date(datetime(2020, 4, 30))
        )

    def test_find_brains_on_operational_objective_parents(self):
        """Test find_brains_on_operational_objective_parents method on operational objective."""
        self.assertEqual(
            [containers_brains[0].Title for containers_brains in find_brains_on_parents(self.oo_15)],
            [
                "Etre une commune qui s'inscrit dans la lign\xc3\xa9e des accords de r\xc3\xa9ductions des gaz "
                "\xc3\xa0 effet de serre afin d'assurer le d\xc3\xa9veloppement durable (OS.10)"
            ]
        )

    def test_find_brains_on_pst_action_parents(self):
        """Test find_brains_on_pst_action_parents method on pst action."""
        self.assertEqual(
            [containers_brains[0].Title for containers_brains in find_brains_on_parents(self.a_16)],
            [
                "R\xc3\xa9duire la consommation \xc3\xa9nerg\xc3\xa9tique des b\xc3\xa2timents communaux de 20% d'ici "
                "2024 (OO.15)",
                "Etre une commune qui s'inscrit dans la lign\xc3\xa9e des accords de r\xc3\xa9ductions des gaz "
                "\xc3\xa0 effet de serre afin d'assurer le d\xc3\xa9veloppement durable (OS.10)"
            ]
        )

    def test_find_brains_on_pst_sub_action_parents(self):
        """Test find_brains_on_pst_sub_action_parents method on pst sub action."""
        self.assertEqual(
            [containers_brains[0].Title for containers_brains in find_brains_on_parents(self.sa_17)],
            [
                "R\xc3\xa9duire la consommation \xc3\xa9nerg\xc3\xa9tique de l'administration communale (A.16)",
                "R\xc3\xa9duire la consommation \xc3\xa9nerg\xc3\xa9tique des b\xc3\xa2timents communaux de 20% d'ici "
                "2024 (OO.15)",
                "Etre une commune qui s'inscrit dans la lign\xc3\xa9e des accords de r\xc3\xa9ductions des gaz "
                "\xc3\xa0 effet de serre afin d'assurer le d\xc3\xa9veloppement durable (OS.10)"
            ]
        )

    def test_find_brains_on_task_parents(self):
        """Test find_brains_on_task_parents method on task."""
        self.assertEqual(
            [containers_brains[0].Title for containers_brains in find_brains_on_parents(self.task)],
            [
                "R\xc3\xa9aliser un audit \xc3\xa9nerg\xc3\xa9tique du b\xc3\xa2timent (SA.17)",
                "R\xc3\xa9duire la consommation \xc3\xa9nerg\xc3\xa9tique de l'administration communale (A.16)",
                "R\xc3\xa9duire la consommation \xc3\xa9nerg\xc3\xa9tique des b\xc3\xa2timents communaux de 20% d'ici "
                "2024 (OO.15)",
                "Etre une commune qui s'inscrit dans la lign\xc3\xa9e des accords de r\xc3\xa9ductions des gaz "
                "\xc3\xa0 effet de serre afin d'assurer le d\xc3\xa9veloppement durable (OS.10)"
            ]
        )

    def test_find_deadlines_on_pst_action_parents(self):
        """Test find_deadlines_on_pst_action_parents method on pst action."""
        self.assertEqual(
            find_deadlines_on_parents(self.a_16, {"operationalobjective": "planned_end_date"}),
            [datetime.date(datetime(2024, 12, 31))]
        )

    def test_find_deadlines_on_pst_sub_action_parents(self):
        """Test find_deadlines_on_pst_sub_action_parents method on pst sub action."""
        self.assertEqual(
            find_deadlines_on_parents(
                self.sa_17,
                {"pstaction": "planned_end_date", "operationalobjective": "planned_end_date"}
            ),
            [datetime.date(datetime(2024, 6, 30)), datetime.date(datetime(2024, 12, 31))]
        )

    def test_find_deadlines_on_task_parents(self):
        """Test find_deadlines_on_task_parents method on task."""
        self.assertEqual(
            find_deadlines_on_parents(
                self.task,
                {
                    "pstsubaction": "planned_end_date",
                    "pstaction": "planned_end_date",
                    "operationalobjective": "planned_end_date"
                }
            ),
            [
                datetime.date(datetime(2020, 6, 30)),
                datetime.date(datetime(2024, 6, 30)),
                datetime.date(datetime(2024, 12, 31))
            ]
        )

    def test_is_smaller_deadline_on_pst_action_parents(self):
        """
        Test is_smaller_deadline_on_pst_action_parents method on pst action.
        context deadline : a_16 = 30/06/2024
        parent deadline : oo_15 = 31/12/2024
        """
        self.assertEqual(self.a_16.planned_end_date, datetime.date(datetime(2024, 6, 30)))
        self.assertEqual(self.oo_15.planned_end_date, datetime.date(datetime(2024, 12, 31)))
        self.assertEqual(
            is_smaller_deadline_on_parents(
                self.a_16,
                {"pstaction": "planned_end_date", "operationalobjective": "planned_end_date"}
            ),
            False
        )
        # context deadline : a_16 = 30/06/2024 => 01/01/2025
        self.a_16.planned_end_date = datetime.date(datetime(2025, 1, 1))
        self.assertEqual(
            is_smaller_deadline_on_parents(
                self.a_16,
                {"pstaction": "planned_end_date", "operationalobjective": "planned_end_date"}
            ),
            True
        )

    def test_is_smaller_deadline_on_pst_sub_action_parents(self):
        """
        Test is_smaller_deadline_on_pst_sub_action_parents method on pst sub action.
        context deadline : sa_17 = 30/06/2020
        parent deadline : a_16 = 30/06/2024, oo_15 = 31/12/2024
        """
        self.assertEqual(self.sa_17.planned_end_date, datetime.date(datetime(2020, 6, 30)))
        self.assertEqual(self.a_16.planned_end_date, datetime.date(datetime(2024, 6, 30)))
        self.assertEqual(self.oo_15.planned_end_date, datetime.date(datetime(2024, 12, 31)))
        self.assertEqual(
            is_smaller_deadline_on_parents(
                self.sa_17,
                {
                    "pstsubaction": "planned_end_date",
                    "pstaction": "planned_end_date",
                    "operationalobjective": "planned_end_date"
                }
            ),
            False
        )
        # context deadline : sa_17 = 30/06/2020 => 30/07/2024
        self.sa_17.planned_end_date = datetime.date(datetime(2024, 7, 30))
        self.assertEqual(
            is_smaller_deadline_on_parents(
                self.sa_17,
                {
                    "pstsubaction": "planned_end_date",
                    "pstaction": "planned_end_date",
                    "operationalobjective": "planned_end_date"
                }
            ),
            True
        )

    def test_is_smaller_deadline_on_task_parents(self):
        """
        Test is_smaller_deadline_on_task_parents method on pst task.
        context deadline : task = 30/04/2020
        parent deadline : sa_17 = 30/06/2020, a_16 = 30/06/2024, oo_15 = 31/12/2024
        """
        self.assertEqual(self.task.due_date, datetime.date(datetime(2020, 4, 30)))
        self.assertEqual(self.sa_17.planned_end_date, datetime.date(datetime(2020, 6, 30)))
        self.assertEqual(self.a_16.planned_end_date, datetime.date(datetime(2024, 6, 30)))
        self.assertEqual(self.oo_15.planned_end_date, datetime.date(datetime(2024, 12, 31)))
        self.assertEqual(
            is_smaller_deadline_on_parents(
                self.task,
                {
                    "task": "due_date",
                    "pstsubaction": "planned_end_date",
                    "pstaction": "planned_end_date",
                    "operationalobjective": "planned_end_date"
                }
            ),
            False
        )
        # context deadline : task = 30/04/2020 => 31/07/2020
        self.task.due_date = datetime.date(datetime(2020, 7, 31))
        self.assertEqual(
            is_smaller_deadline_on_parents(
                self.task,
                {
                    "task": "due_date",
                    "pstsubaction": "planned_end_date",
                    "pstaction": "planned_end_date",
                    "operationalobjective": "planned_end_date"
                }
            ),
            True
        )
