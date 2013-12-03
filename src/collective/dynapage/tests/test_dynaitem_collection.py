# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import queryUtility, createObject
from collective.dynapage.tests.base import MYPRODUCT_INTEGRATION_TESTING
from collective.dynapage.tests.base import MYPRODUCT_FUNCTIONAL_TESTING
from collective.dynapage.dynacollection import IDynaCollection
from collective.dynapage.interfaces import IDynaItem, IDynaItemPosition, IListsItem
from plone.dexterity.interfaces import IDexterityFTI
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
        parent = self.createDummyParent(self.portal)
        self.createDummyContent('News Item', 10, parent)
        self.createDummyContent('Event', 10, parent)

    def createDummyContent(self, content_type, amount, parent):
        id_base = '%s-dummy-article' % content_type.split(' ')[0].lower()
        title_base = u'Dummy article'
        description = u'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        body_text = u'Foobar'

        counter = 0
        while counter < amount:
            id = '%s-%s' % (id_base, str(counter))
            title = u'%s %s' % (title_base, str(counter))
            parent.invokeFactory(content_type, id=id, title=title)
            obj = parent[id]
            obj.setDescription(description)
            obj.setText(body_text)
            obj.reindexObject()
            counter += 1

    def createDummyParent(self, parent):
        parent.invokeFactory("Folder", id='news', title=u'News')
        obj = parent['news']
        obj.reindexObject()
        return obj

    def test_create_dynaitem(self):
        self.portal.invokeFactory('collective.dynapage', id='dynapage',
                                  title=u'Dynapage')
        obj = self.portal['dynapage']
        obj.invokeFactory('collective.dynaitem.collection', id='collection',
                          title=u'Collection')
        self.assertTrue('collection' in obj.objectIds())
        collection = obj['collection']
        self.failUnless(IDynaCollection.providedBy(collection))
        self.failUnless(IDynaItem.providedBy(collection))
        self.failUnless(IDynaItemPosition.providedBy(collection))
        self.failUnless(IListsItem.providedBy(collection))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='collective.dynaitem.collection')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='collective.dynaitem.collection')
        schema = fti.lookupSchema()
        self.assertEquals(IDynaCollection, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='collective.dynaitem.collection')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IDynaCollection.providedBy(new_object))

    def test_view(self):
        self.portal.invokeFactory('collective.dynapage', id='dynapage',
                                  title=u'Dynapage')
        obj = self.portal['dynapage']
        obj.invokeFactory('collective.dynaitem.collection', 'dynacollection')
        d1 = obj['dynacollection']
        view = d1.restrictedTraverse('@@view')
        brains = view.search()
        self.assertEquals(0, len(brains))


class FunctionalTest(unittest.TestCase):
    layer = MYPRODUCT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

