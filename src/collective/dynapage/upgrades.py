# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


def upgrade1to2(self):
    setup_tool = getToolByName(self, "portal_setup")
    setup_tool.runAllImportStepsFromProfile(
        "profile-collective.dynapage:upgrade1to2")
    return "Upgraded collective.dynapage."
