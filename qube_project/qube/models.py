from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    RelationshipTo, StructuredRel, DateProperty
)
from datetime import date

class MemberRel(StructuredRel):
    role = StringProperty()

class UserNode(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    email = StringProperty(unique_index=True, required=True)
    password = StringProperty(required=True)  # przechowujemy zahaszowane hasło
    first_name = StringProperty()             # opcjonalnie
    last_name = StringProperty()              # opcjonalnie
    groups = RelationshipTo('Group', 'BELONGS_TO')

class Group(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    leader = RelationshipTo('UserNode', 'LEADS')
    members = RelationshipTo('UserNode', 'HAS_MEMBER', model=MemberRel)
    tasks = RelationshipTo('Task', 'HAS_TASK')

class Task(StructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty(required=True)
    description = StringProperty()
    priority = StringProperty(default="low")      # "low", "medium", "high"
    status = StringProperty(default="Oczekujące")      # "pending", "in-progress", "done"
    due_date = DateProperty()                       # data oddania (może być None)
    assigned_to = RelationshipTo('UserNode', 'ASSIGNED_TO')

    def days_left(self):
        if not self.due_date:
            return None
        return (self.due_date - date.today()).days

    def get_status_display(self):
        mapping = {
            'pending': 'Oczekujące',
            'in-progress': 'W trakcie',
            'done': 'Zakończone'
        }
        return mapping.get(self.status, self.status)