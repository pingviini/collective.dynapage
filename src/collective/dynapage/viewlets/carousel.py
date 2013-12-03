from five import grok
from collective.dynapage.dynapage import IDynapage
from collective.dynapage.interfaces import ICarouselItem,\
                                           IDynapageBrowserLayer,\
                                           IDynapageView
from plone.app.layout.viewlets.interfaces import IAboveContent
from plone.memoize import view, ram
from random import randint, shuffle


class CarouselBase:

    @property
    @view.memoize
    def brains(self):
        results = self.context.getFolderContents({
            'object_provides': ICarouselItem.__identifier__,
            'sort_on': 'getObjPositionInParent',
            'sort_order': 'ascending'})

        return results

    @property
    def folderly(self):
        return [b.id for b in self.brains]

    @property
    @ram.cache(lambda m, self: self.folderly)
    def randomly(self):
        randomly = []
        indexes = range(len(self.brains))
        shuffle(indexes)
        while indexes:
            randomly.append(self.brains[indexes.pop()].id)
        return randomly

    @property
    @ram.cache(lambda m, self: str(self.context.modified()))
    def delay(self):
        delay = self.context.changeDelay
        if delay > 0 and len(self.brains) > 1:# and self.context.overridingContent is None:
            return delay
        else:
            return None

    @property
    @view.memoize
    def content(self):
       # 1. get overriding content
        try:
            content = self.context.overridingContent
        except AttributeError:
            content = None

        # 2. get explicitly queried content
        uid = self.request.get("id", None)
        if not content and uid in self.folderly:
            content = self.brains[self.folderly.index(uid)].getObject()

        # 3. if no overriding was found, proceed to select content
        if not content and self.brains:

            # get the changing method
            method = self.context.changingMethod

            # if there"s only one content item, discard previous
            previous = len(self.brains) > 1\
                and self.request.get("previous", None) or None

            # if delay is set to zero for randomly change, be really random
            if method == "randomly" and not self.delay:
                selection = self.brains[
                    randint(0, len(self.brains) - 1)]

            # select the next selection in random order
            elif method == "randomly":
                if previous in self.randomly:
                    next = self.randomly.index(previous) + 1
                    if next < len(self.brains):
                        selection = self.brains[\
                            self.folderly.index(self.randomly[next])]
                    else:
                        selection = self.brains[\
                            self.folderly.index(self.randomly[0])]
                else:
                    selection = self.brains[\
                        self.folderly.index(self.randomly[0])]

            # select the next selection in folder order
            elif method == "folderly":
                if previous in self.folderly:
                    next = self.folderly.index(previous) + 1
                    if next < len(self.brains):
                        selection = self.brains[next]
                    else:
                        selection = self.brains[0]
                else:
                    selection = self.brains[0]

            # otherwise
            else:
                selection = self.brains[0]

            content = selection.getObject()

        # 4. return the content
        return content or None

    @property
    #@ram.cache(lambda m, self: self.content and self.content.Description())
    def target(self):
        #if self.content:
        #    candidates = [match[0] for match
        #                  in LINK_REGEXP.findall(self.content.Description())]
        #    return candidates and candidates[0] or None
        return None


class CarouselViewlet(grok.Viewlet, CarouselBase):
    grok.context(IDynapage)
    grok.layer(IDynapageBrowserLayer)
    grok.viewletmanager(IAboveContent)

    def available(self):
        """ Check if we are in a specific content type.

        Check that the Dexerity content type has a certain
        behavior set on it through Dexterity settings panel.
        """
        if self.brains and self.context.active:
            return True
        else:
            return False
        return False

    @property
    def overridingContent(self):
        try:
            if self.context.overridingContent:
                return True
            else:
                return False
        except AttributeError:
            return False
        return False


class CarouselView(grok.View, CarouselBase):
    grok.context(IDynapage)
    grok.require('zope2.View')
    grok.name('carouselview')
    grok.implements(IDynapageView)
