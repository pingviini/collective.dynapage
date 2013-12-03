# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import queryUtility, createObject
from zope.intid.interfaces import IIntIds
from z3c.relationfield import RelationValue
from collective.dynapage.tests.base import MYPRODUCT_INTEGRATION_TESTING
from collective.dynapage.tests.base import MYPRODUCT_FUNCTIONAL_TESTING
from collective.dynapage.dynapage import IDynapage
from plone.dexterity.interfaces import IDexterityFTI
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from Products.CMFCore.utils import getToolByName


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
        # wf_tool = getToolByName(parent, 'portal_workflow')

        counter = 0
        while counter < amount:
            id = '%s-%s' % (id_base, str(counter))
            title = u'%s %s' % (title_base, str(counter))
            parent.invokeFactory(content_type, id=id, title=title)
            obj = parent[id]
            #obj.setTitle(title)
            obj.setDescription(description)
            obj.setText(body_text)

            # wf_tool.doActionFor(obj, 'publish')
            obj.reindexObject()
            counter += 1

    def createDummyParent(self, parent):
        parent.invokeFactory("Folder", id='news', title=u'News')
        obj = parent['news']

        # wf_tool = getToolByName(parent, 'portal_workflow')
        # wf_tool.doActionFor(obj, 'publish')
        obj.reindexObject()
        return obj

    def test_is_dynapage_activated(self):
        portal_types = getToolByName(self.portal, 'portal_types')
        self.assertTrue('collective.dynapage' in portal_types.objectIds())
        self.assertTrue('collective.dynaitem.collection' in\
                        portal_types.objectIds())
        self.assertTrue('collective.dynaitem.image' in portal_types.objectIds())
        self.assertTrue('collective.dynaitem.feed' in portal_types.objectIds())

    def test_is_dexterity_activated(self):
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue('plone.app.dexterity' in [addon['id'] for addon in\
            qi.listInstalledProducts()])

    def test_is_javascript_registered(self):
        pj = getToolByName(self.portal, 'portal_javascripts')
        self.assertTrue('++resource++collective.dynapage/dynacarousel.js' in\
            pj.getResourceIds())

    def test_is_css_registered(self):
        ps = getToolByName(self.portal, 'portal_css')
        self.assertTrue('++resource++collective.dynapage/dynapage.css' in\
            ps.getResourceIds())

    def test_intid_values(self):
        """
        Test relationvalues & intids in scenarios where collective.dynapage gets
        reinstalled different ways.
        """
        intid = queryUtility(IIntIds)
        id = intid.queryId(self.portal['news'])
        rel = RelationValue(id)
        self.assertTrue(id > 0)
        self.assertEqual(id, rel.to_id)

        ps = getToolByName(self.portal, 'portal_setup')
        ps.runAllImportStepsFromProfile('profile-collective.dynapage:default')
        newid = intid.queryId(self.portal['news'])
        rel1 = RelationValue(newid)
        self.assertEqual(id, newid)
        self.assertEqual(id, rel1.to_id)

        qi = getToolByName(self.portal, 'portal_quickinstaller')
        qi.reinstallProducts(['collective.dynapage'])
        newid = intid.queryId(self.portal['news'])
        rel2 = RelationValue(newid)
        self.assertEqual(id, newid)
        self.assertEqual(id, rel2.to_id)

        self.assertTrue(rel == rel1 == rel2)

    def test_create_dynapage(self):
        self.portal.invokeFactory('collective.dynapage', id='dynapage',
                                  title=u'Dynapage')
        obj = self.portal['dynapage']
        self.assertTrue('dynapage' in self.portal.objectIds())
        self.failUnless(IDynapage.providedBy(obj))

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='collective.dynapage')
        self.assertNotEquals(None, fti)

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='collective.dynapage')
        schema = fti.lookupSchema()
        self.assertEquals(IDynapage, schema)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='collective.dynapage')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IDynapage.providedBy(new_object))

    def test_view(self):
        self.portal.invokeFactory('collective.dynapage', 'dynapage')
        d1 = self.portal['dynapage']
        view = d1.restrictedTraverse('@@view')
        feeds = view.feeds
        self.assertEquals(0, len(feeds))


class FunctionalTest(unittest.TestCase):
    layer = MYPRODUCT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

