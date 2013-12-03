from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile


class MyProduct(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.dynapage
        self.loadZCML(name='configure.zcml', package=collective.dynapage)
        self.loadZCML(package=collective.dynapage)

        # Install product and call its initialize() function
        # z2.installProduct(app, 'collective.dynapage')
        # Note: you can skip this if my.product is not a Zope 2-style
        # product, i.e. it is not in the Products.* namespace and it
        # does not have a <five:registerPackage /> directive in its
        # configure.zcml.

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'collective.dynapage:default')

    def tearDownZope(self, app):
        # Uninstall product
        # z2.uninstallProduct(app, 'collective.dynapage')
        # Note: Again, you can skip this if my.product is not a Zope 2-
        # style product
        pass


MYPRODUCT_FIXTURE = MyProduct()
MYPRODUCT_INTEGRATION_TESTING = IntegrationTesting(bases=(MYPRODUCT_FIXTURE,), name="collective.dynapage:Integration")
MYPRODUCT_FUNCTIONAL_TESTING = FunctionalTesting(bases=(MYPRODUCT_FIXTURE,), name="collective.dynapage:Functional")
