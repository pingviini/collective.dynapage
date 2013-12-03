from plone.app.relationfield.widget import RelationListDataManager, RelationDataManager
from z3c.relationfield.interfaces import IRelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield.relation import RelationValue

def relation_list_set(self, value):
    """
    Sets the relationship target. Monkeypatches issues in original
    RelationListDataManager where manager assumes that every object has
    intid.
    """

    value = value or []
    new_relationships = []
    intids = getUtility(IIntIds)
    for item in value:
        # otherwise create one
        try:
            to_id = intids.getId(item)
        except KeyError:
            to_id = intids.register(item)
        new_relationships.append(RelationValue(to_id))
    super(RelationListDataManager, self).set(new_relationships)

RelationListDataManager.set = relation_list_set


def relation_set(self, value):
    """Sets the relationship target"""
    if value is None:
        return super(RelationDataManager, self).set(None)

    current = None
    try:
        current = super(RelationDataManager, self).get()
    except AttributeError:
        pass
    intids = getUtility(IIntIds)
    try:
        to_id = intids.getId(value)
    except KeyError:
        to_id = intids.register(value)
    if IRelationValue.providedBy(current):
        # If we already have a relation, just set the to_id
        current.to_id = to_id
    else:
        # otherwise create a relationship
        rel = RelationValue(to_id)
        super(RelationDataManager, self).set(rel)

RelationDataManager.set = relation_set
