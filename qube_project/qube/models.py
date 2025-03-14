from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo, StructuredRel
)

# Relacja użytkownika w grupie z dodatkową właściwością "role"
class MemberRel(StructuredRel):
    role = StringProperty()

# Model użytkownika
class UserNode(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    email = StringProperty(unique_index=True, required=True)
    groups = RelationshipTo('Group', 'BELONGS_TO')

# Model grupy
class Group(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    leader = RelationshipTo('UserNode', 'LEADS')  # ✅ Poprawka: zwraca jednego użytkownika
    members = RelationshipTo('UserNode', 'HAS_MEMBER', model=MemberRel)  # ✅ Możesz usunąć model jeśli nie potrzebujesz "role"
    tasks = RelationshipTo('Task', 'HAS_TASK')

# Model zadania
class Task(StructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty(required=True)
    description = StringProperty()
    status = StringProperty(choices={"pending": "Pending", "in-progress": "In Progress", "done": "Done"}, default="pending")  # ✅ Poprawka: statusy jako wybór
    assigned_to = RelationshipTo('UserNode', 'ASSIGNED_TO')
