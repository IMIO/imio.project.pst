# -*- coding: utf-8 -*-
from imio.project.pst.interfaces import IImioPSTProject
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes


def adaptConstrainTypesForProjectSpace(obj, event):
    """When a projectspace is created, if it is not the PST, we constrain types to ('project', )"""

    if not IImioPSTProject.providedBy(obj):
        behaviour = ISelectableConstrainTypes(obj)
        behaviour.setConstrainTypesMode(1)
        behaviour.setLocallyAllowedTypes(['project', ])
        behaviour.setImmediatelyAddableTypes(['project', ])
