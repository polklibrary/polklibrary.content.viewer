# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from polklibrary.content.viewer.testing import POLKLIBRARY_CONTENT_VIEWER_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that polklibrary.content.viewer is properly installed."""

    layer = POLKLIBRARY_CONTENT_VIEWER_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if polklibrary.content.viewer is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('polklibrary.content.viewer'))

    def test_browserlayer(self):
        """Test that IPolklibraryContentViewerLayer is registered."""
        from polklibrary.content.viewer.interfaces import IPolklibraryContentViewerLayer
        from plone.browserlayer import utils
        self.assertIn(IPolklibraryContentViewerLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = POLKLIBRARY_CONTENT_VIEWER_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['polklibrary.content.viewer'])

    def test_product_uninstalled(self):
        """Test if polklibrary.content.viewer is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled('polklibrary.content.viewer'))

    def test_browserlayer_removed(self):
        """Test that IPolklibraryContentViewerLayer is removed."""
        from polklibrary.content.viewer.interfaces import IPolklibraryContentViewerLayer
        from plone.browserlayer import utils
        self.assertNotIn(IPolklibraryContentViewerLayer, utils.registered_layers())
