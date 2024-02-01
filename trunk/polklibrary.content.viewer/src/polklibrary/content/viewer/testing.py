# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import polklibrary.content.viewer


class PolklibraryContentViewerLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=polklibrary.content.viewer)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'polklibrary.content.viewer:default')


POLKLIBRARY_CONTENT_VIEWER_FIXTURE = PolklibraryContentViewerLayer()


POLKLIBRARY_CONTENT_VIEWER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(POLKLIBRARY_CONTENT_VIEWER_FIXTURE,),
    name='PolklibraryContentViewerLayer:IntegrationTesting'
)


POLKLIBRARY_CONTENT_VIEWER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(POLKLIBRARY_CONTENT_VIEWER_FIXTURE,),
    name='PolklibraryContentViewerLayer:FunctionalTesting'
)


POLKLIBRARY_CONTENT_VIEWER_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        POLKLIBRARY_CONTENT_VIEWER_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PolklibraryContentViewerLayer:AcceptanceTesting'
)
