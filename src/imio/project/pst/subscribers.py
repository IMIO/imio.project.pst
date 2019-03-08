# -*- coding: utf-8 -*-
from imio.project.pst.interfaces import IActionDashboardBatchActions
from imio.project.pst.interfaces import IImioPSTProject
from imio.project.pst.interfaces import IOODashboardBatchActions
from imio.project.pst.interfaces import IOSDashboardBatchActions
from imio.project.pst.interfaces import ITaskDashboardBatchActions
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from zope.interface import alsoProvides


def projectspace_created(obj, event):
    """When a projectspace is created, if it is not the PST, we constrain types to ('project', )"""

    alsoProvides(obj, IOSDashboardBatchActions)

    if not IImioPSTProject.providedBy(obj):
        behaviour = ISelectableConstrainTypes(obj)
        behaviour.setConstrainTypesMode(1)
        behaviour.setLocallyAllowedTypes(['project', ])
        behaviour.setImmediatelyAddableTypes(['project', ])


def strategic_created(obj, event):
    """  """
    alsoProvides(obj, IOODashboardBatchActions)


def operational_created(obj, event):
    """  """
    alsoProvides(obj, IActionDashboardBatchActions)


def pstaction_created(obj, event):
    """  """
    alsoProvides(obj, ITaskDashboardBatchActions)
