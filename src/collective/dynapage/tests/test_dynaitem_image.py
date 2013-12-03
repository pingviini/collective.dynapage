# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import queryUtility, createObject
from collective.dynapage.tests.base import MYPRODUCT_INTEGRATION_TESTING
from collective.dynapage.tests.base import MYPRODUCT_FUNCTIONAL_TESTING
from collective.dynapage.interfaces import IDynaItem, ICarouselItem
from plone.dexterity.interfaces import IDexterityFTI
from collective.dynapage.dynaimage import IDynaImage
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
#from Products.CMFCore.utils import getToolByName


class IntegrationTest(unittest.TestCase):
    layer = MYPRODUCT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        # login
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Owner'])

    def test_create_dynaitem(self):
        self.portal.invokeFactory('collective.dynapage', id='dynapage',
                                  title=u'Dynapage')
        obj = self.portal['dynapage']
        obj.invokeFactory('collective.dynaitem.image', id='image1', title=u"Image 1")
        self.assertTrue('image1' in obj.objectIds())
        image = obj['image1']
        self.failUnless(IDynaItem.providedBy(image))
        self.failUnless(ICarouselItem.providedBy(image))
        self.failUnless(IDynaImage.providedBy(image))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='collective.dynaitem.image')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='collective.dynaitem.image')
        schema = fti.lookupSchema()
        self.assertEquals(IDynaImage, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='collective.dynaitem.image')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IDynaImage.providedBy(new_object))

    def test_view(self):
        self.portal.invokeFactory('collective.dynapage', id='dynapage',
                                  title=u'Dynapage')
        obj = self.portal['dynapage']
        obj.invokeFactory('collective.dynaitem.image', 'dynaimage')
        d1 = obj['dynaimage']
        view = d1.restrictedTraverse('@@view')
        self.failUnless(view)


class FunctionalTest(unittest.TestCase):
    layer = MYPRODUCT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

