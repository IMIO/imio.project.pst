# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from imio.project.pst.testing import IntegrationTestCase


class TestInstall(IntegrationTestCase):
    """Test installation of imio.project.pst into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = self.portal.portal_quickinstaller

    def test_product_installed(self):
        """Test if imio.project.pst is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('imio.project.pst'))

    def test_uninstall(self):
        """Test if imio.project.pst is cleanly uninstalled."""
        self.installer.uninstallProducts(['imio.project.pst'])
        self.assertFalse(self.installer.isProductInstalled('imio.project.pst'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IImioProjectPSTLayer is registered."""
        from imio.project.pst.interfaces import IImioProjectPSTLayer
        from plone.browserlayer import utils
        self.failUnless(IImioProjectPSTLayer in utils.registered_layers())
