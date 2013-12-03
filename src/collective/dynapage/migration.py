import transaction
from five import grok
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName
from z3c.relationfield import RelationValue
from zope.app.intid.interfaces import IIntIds
from zope.component import queryUtility

from plone.app.textfield.value import RichTextValue

from plone.uuid.interfaces import IMutableUUID
from Products.Archetypes.config import UUID_ATTR
from plone.uuid.interfaces import IUUID
from plone.dexterity.utils import createContentInContainer

from Products.CMFCore.utils import getToolByName
from DateTime import DateTime


def changeWorkflowState(content, state_id, acquire_permissions=False,
                        portal_workflow=None, **kw):
    """Change the workflow state of an object
    @param content: Content obj which state will be changed
    @param state_id: name of the state to put on content
    @param acquire_permissions: True->All permissions unchecked and on riles and
                                acquired
                                False->Applies new state security map
    @param portal_workflow: Provide workflow tool (optimisation) if known
    @param kw: change the values of same name of the state mapping
    @return: None
    """

    if portal_workflow is None:
        portal_workflow = getToolByName(content, 'portal_workflow')

    # Might raise IndexError if no workflow is associated to this type
    wf_def = portal_workflow.getWorkflowsFor(content)[0]
    wf_id= wf_def.getId()

    wf_state = {
        'action': None,
        'actor': None,
        'comments': "Setting state to %s" % state_id,
        'review_state': state_id,
        'time': DateTime(),
        }

    # Updating wf_state from keyword args
    for k in kw.keys():
        # Remove unknown items
        if not wf_state.has_key(k):
            del kw[k]
    if kw.has_key('review_state'):
        del kw['review_state']
    wf_state.update(kw)

    portal_workflow.setStatusOf(wf_id, content, wf_state)

    if acquire_permissions:
        # Acquire all permissions
        for permission in content.possible_permissions():
            content.manage_permission(permission, acquire=1)
    else:
        # Setting new state permissions
        wf_def.updateRoleMappingsFor(content)

    # Map changes to the catalogs
    content.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
    return


class MigrateDynapage(grok.View):
    """Replace all Products.JYUDynaPage content with new collective.dynapage."""
    grok.context(IPloneSiteRoot)
    grok.name("migrate-dynapage")
    grok.require("cmf.ManagePortal")

    def update(self):

        lists = ['first', 'second', 'third', 'fourth']
        attributes = ['_list_active', '_list_style', '_list_position',
                      '_list_title', '_list_order_by', '_list_order',
                      '_list_types', '_list_state', '_list_custom_view_fields',
                      '_list_keywords', '_list_items', '_list_path',
                      '_list_rss_title']

        pc = getToolByName(self.context, 'portal_catalog')
        wf = getToolByName(self.context, 'portal_workflow')

        query = {'portal_type': 'DynaPage'}
        brains = pc.queryCatalog(query)
        self.count = len(brains)


        for content in [brain.getObject() for brain in brains]:
            print content.absolute_url()

            parent = content.aq_parent

            title = content.title
            description = content.description
            text = content.text

            review_state = wf.getStatusOf(wf.getChainFor(content)[0], content)['review_state']
            inherit_image = content.inheritImage
            keywords = content.Subject()
            active_lists = self.getActiveLists(lists, content)
            active_lists_values = self.getActiveListsValues(attributes,
                                                            active_lists,
                                                            content)

            content.wl_clearLocks()

            tmp_id = content.id + "-tmp"
            parent.invokeFactory('Folder', tmp_id, title = content.title)
            tmp = parent[tmp_id]
            self.getObjectsFromContainer(content, tmp)

            # Delete old content and store the UUID
            old_uuid = IUUID(content)

            # Remove new and old object-uid from uid-catalog
            content._uncatalogUID(self.context)

            # set UID none, so it won't be checked by plone.app.integrity
            setattr(content, UUID_ATTR, None)
            assert getattr(content, UUID_ATTR) == None

            new_id = content.id
            parent.manage_delObjects([content.id])

            try:
                parent.invokeFactory(
                    'collective.dynapage',
                    new_id,
                    title = title,
                    description = description,
                    text = RichTextValue(text, 'text/safe-html', 'text/html')
                )
            except:
                print "*"*40
                print parent.absolute_url()

            new = parent[new_id]
            new.setSubject(keywords)
            new.reindexObject()

            self.getObjectsFromContainer(tmp, new)
            parent.manage_delObjects([tmp_id])

            new.reindexObject()
            self.createCollections(new, active_lists_values)

            # set old UID into the new one
            IMutableUUID(new).set(old_uuid)

            # get archetypes uid_catalog
            uid_catalog = getToolByName(self.context, "uid_catalog")

            # index the new object with old uid
            uid_catalog.catalog_object(
                new, "/".join(new.getPhysicalPath()))

            if inherit_image:
                try:
                    if not new.overridingContent:
                        iid = queryUtility(IIntIds)
                        image = content['etusivu.jpg']
                        try:
                            etusivu_iid = iid.getId(image)
                        except KeyError:
                            etusivu_iid = iid.register(image)
                            new.overridingContent = RelationValue(etusivu_iid)
                except:
                    pass

            try:
                delay = new.changeDelay
            except AttributeError:
                new.changeDelay = 10

            try:
                override = new.overridingContent
            except AttributeError:
                new.overridingContent = None

            try:
                method = new.changingMethod
            except AttributeError:
                new.changingMethod = u'folderly'

            try:
                method = new.showNavigation
            except AttributeError:
                new.showNavigation = True

            try:
                changeWorkflowState(new, review_state)
            except:
                print "We're in trouble here..."


    def getObjectsFromContainer(self, container, new):
        for obj in container.getFolderContents():
            obj = obj.getObject()
            new.manage_pasteObjects(container.manage_cutObjects(obj.id))
            if obj.id == 'etusivu.jpg':
                # Set etusivu.jpg as overridingContent
                iid = queryUtility(IIntIds)
                try:
                    etusivu_iid = iid.getId(new[obj.id])
                except KeyError:
                    etusivu_iid = iid.register(new[obj.id])
                new.overridingContent = RelationValue(etusivu_iid)
                new.changeDelay = 10

    def createCollections(self, new, listdata):

        wf_tool = getToolByName(self.context, 'portal_workflow')

        for data in listdata.values():
            try:
                obj = createContentInContainer(new, 'collective.dynaitem.collection',
                                     title=data['title'])
            except:
                obj = createContentInContainer(new, 'collective.dynaitem.collection',
                                     title=new.title)

            if data['reversed_order']:
                obj.reversed_order = True
            else:
                obj.reversed_order = False

            if not data['search_path']:
                iid = queryUtility(IIntIds)
                try:
                    new_id = iid.getId(new.aq_parent)
                except KeyError:
                    new_id = iid.register(new.aq_parent)
                path_obj = RelationValue(new_id)
                print "No path, created new iid to parent: ", str(path_obj.to_path)
                obj.search_path = [path_obj]
            else:
                folders = []
                iid = queryUtility(IIntIds)
                for ref in data['search_path']:
                    try:
                        ref_id = iid.getId(self.context.reference_catalog.lookupObject(ref))
                    except KeyError:
                        try:
                            ref_id = iid.register(self.context.reference_catalog.lookupObject(ref))
                        except TypeError:
                            # We're in root - No intids here.
                            ref_id = iid.getId(new)
                    folders.append(ref_id)
                obj.search_path = [RelationValue(folder) for folder in folders]

            if data['keywords']:
                keywords = self.checkKeywords(data['keywords'])
            else:
                keywords = ()

            obj.rss_title = data['rss_title']
            obj.order_by = data['order_by']
            obj.title = data['title']
            obj.types = data['types']
            obj.keywords = keywords
            obj.workflow_states = data['workflow_states']
            obj.limit = data['limit']
            obj.reindexObject()

            # We've migrating only active lists, so we assume we can publish
            # them.
            wf_tool.doActionFor(obj, 'publish')

    def checkKeywords(self, keywords):
        pc = getToolByName(self.context, 'portal_catalog')
        tmp = tuple()
        for keyword in keywords:
            res = pc({'Subject': keyword})
            if len(res) > 0:
                tmp += keyword,
        return tmp

    def getActiveLists(self, lists, content):
        active_list = []
        for i in lists:
            attr_name = i + '_list_active'
            if content[attr_name] == True:
                active_list.append(attr_name)
        return active_list

    def getActiveListsValues(self, attributes, active_lists, content):
        data = {}

        for active_list in active_lists:
            listnumber = active_list.split('_')[0]
            tmp_dict = data[listnumber] = {}
            for listattribute in attributes:
                attr_name = listnumber + listattribute
                converted_name =self.convertToNewAttr(attr_name)
                tmp_dict[converted_name] = content[attr_name]

        return data

    def convertToNewAttr(self, attr):
        new_attrs = {
            'list_position': 'position',
            'list_title': 'title',
            'list_order_by': 'order_by',
            'list_order': 'reversed_order',
            'list_types': 'types',
            'list_state': 'workflow_states',
            'list_keywords': 'keywords',
            'list_items': 'limit',
            'list_path': 'search_path',
            'list_rss_title': 'rss_title'}

        keys = new_attrs.keys()
        # Sort list so we get list_order_by always before list_order.
        keys.sort(reverse=True)
        for i in keys:
            if i in attr:
                return new_attrs[i]
        return attr.split('_')[-1]

    def render(self):
        return "Migrated %s dynapages." % self.count
