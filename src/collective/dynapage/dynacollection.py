from urllib import quote

from five import grok
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from z3c.relationfield.schema import RelationChoice, RelationList
from z3c.formwidget.query.interfaces import IQuerySource

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IContextSourceBinder
from zope import schema
from zope.interface import implements
from zope.security import checkPermission

from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget
from plone.directives import form
from plone.dexterity.content import Item
from plone.formwidget.contenttree import ObjPathSourceBinder

from collective.dynapage.interfaces import IDynaItemPosition,\
                                           IListsItem,\
                                           IDynaCollectionView,\
                                           IDynaRSSView
from collective.dynapage import _


class KeywordSource(object):
    implements(IQuerySource)

    def __init__(self, context):
        self.context = context
        catalog = getToolByName(context, 'portal_catalog')
        self.keywords = catalog.uniqueValuesFor('Subject')

        def safe_str(s):
            if type(s) == unicode:
                return s.encode("utf-8", "replace")
            else:
                return s

        def safe_unicode(s):
            if type(s) == str:
                return unicode(s, "utf-8", "replace")
            else:
                return s

        # XXX: plone.z3cform monkeypatches z3c.forms to decode
        # all form values in query to unicode; in short, one cannot
        # use non-ascii characters in tokens (z3c.form expects tokens
        # to be encoded strings, but plone.z3cform breaks this)

        self.vocab = SimpleVocabulary([
            SimpleTerm(safe_unicode(x), quote(safe_str(x)), safe_unicode(x))
            for x in self.keywords])

    def __contains__(self, term):
        return self.vocab.__contains__(term)

    def __iter__(self):
        return self.vocab.__iter__()

    def __len__(self):
        return self.vocab.__len__()

    def getTerm(self, value):
        def safe_unicode(s):
            if type(s) == str:
                return unicode(s, "utf-8", "replace")
            else:
                return s
        return self.vocab.getTerm(safe_unicode(value))

    def getTermByToken(self, value):
        return self.vocab.getTermByToken(value)

    def search(self, query_string):
        q = query_string.lower()
        return [self.getTerm(kw) for kw in self.keywords if q in kw.lower()]


class KeywordSourceBinder(object):
    implements(IContextSourceBinder)

    def __call__(self, context):
        return KeywordSource(context)


class IDynaCollection(IDynaItemPosition, form.Schema):
    """Dynapage collection."""

    rss_title = schema.TextLine(
        title=_(u"RSS feeds title"),
        required=False,)

    order_by = schema.Choice(
        title=_(u"Order by"),
        required=False,
        values=["sortable_title", "created", "effective", "start"],
        default="created")

    reversed_order = schema.Bool(
        title=_(u"Reversed order"),
        required=False,
        default=False)

    types = schema.Tuple(
        title=_(u"Content types to search for"),
        required=True,
        value_type=schema.Choice(
            vocabulary='plone.app.vocabularies.UserFriendlyTypes'),
        default=('News Item',))

    search_path = RelationList(
        title=_(u"Select paths where content items are searched"),
        value_type=RelationChoice(
            title=_(u"Related"),
            source=ObjPathSourceBinder()),
        required=True,
        )

    form.widget(keywords=AutocompleteMultiFieldWidget)
    keywords = schema.Tuple(
        title=_(u"Keywords"),
        description=_(u"Enter beginning of the keyword to see available keywords."),
        value_type=schema.Choice(
            source=KeywordSourceBinder(),
            required=False),
        required=False,
        )

    workflow_states = schema.Tuple(
        title=_(u"Select workflow states to search for"),
        required=False,
        value_type=schema.Choice(
            vocabulary='plone.app.vocabularies.WorkflowStates'),
        default=('published',))

    limit = schema.Int(
        title=_(u"Amount of results to show"),
        required=True,
        default=5)


class DynaCollection(Item):
    """DynaCollection class"""
    grok.implements(IListsItem)


class View(grok.View):
    grok.context(IDynaCollection)
    grok.implements(IDynaCollectionView)
    grok.require('zope2.View')
    def search(self):
        pc = getToolByName(self.context, 'portal_catalog')
        limit = self.context.limit
        order = self._getOrder()
        search_path = self._getSearchPath()
        now = DateTime()

        querydict = {
            'portal_type': self.context.types,
            'review_state': self.context.workflow_states,
            'sort_on': self.context.order_by,
            'sort_order': order,
            'sort_limit': limit,
            'effectiveRange': now,
        }

        if self.context.keywords:
            querydict['Subject'] = self.context.keywords
        if search_path:
            querydict['path'] = search_path

        results = pc.searchResults(querydict)[:limit]

        return results

    def _getOrder(self):
        if self.context.reversed_order:
            return 'descending'
        else:
            return 'ascending'

    def _getSearchPath(self):
        if self.context.search_path:
            paths = []
            for path in self.context.search_path:
                paths.append(path.to_path)
            return paths
        else:
            return None


class ListView(View, grok.View):
    grok.name('listview')

    def canModify(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)


class RSSView(View, grok.View):
    """View for displaying collection results as RSS feed"""

    grok.name('RSS')

    @property
    def title(self):
        return self.context.rss_title or self.context.title
