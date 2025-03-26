# qube/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from qube.models import Group, Task, UserNode, MemberRel
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = "Seed database with sample data: 10 users, 4 groups, 20 tasks."

    def handle(self, *args, **options):
        self.stdout.write("Rozpoczynam seeding danych...")

        # 1. Tworzymy 10 użytkowników Django i odpowiadające im węzły Neo4j
        for i in range(1, 11):
            username = f"user{i}"
            email = f"user{i}@example.com"
            password = "zaq1@WSX"
            user, created = User.objects.get_or_create(username=username, defaults={"email": email})
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f"Utworzono użytkownika {username} w systemie Django.")
            else:
                self.stdout.write(f"Użytkownik {username} już istnieje.")

            # Sprawdzamy, czy węzeł UserNode istnieje – jeśli nie, tworzymy go.
            try:
                UserNode.nodes.get(username=username)
            except UserNode.DoesNotExist:
                UserNode(username=username, email=email).save()
                self.stdout.write(f"Utworzono węzeł UserNode dla {username}.")

        # 2. Tworzymy 4 grupy; liderami są user1, user2, user3, user4
        groups = {}
        for i in range(1, 5):
            group_name = f"group{i}"
            leader_username = f"user{i}"
            leader_node = UserNode.nodes.get(username=leader_username)
            group = Group(name=group_name).save()
            group.leader.connect(leader_node)
            group.members.connect(leader_node)
            groups[group_name] = group
            self.stdout.write(f"Utworzono grupę {group_name} z liderem {leader_username}.")

        # (Opcjonalnie) Dodajemy dodatkowych członków do każdej grupy – wybieramy losowo 2 osoby spośród user5 do user10
        for group in groups.values():
            potential_members = [UserNode.nodes.get(username=f"user{i}") for i in range(5, 11)]
            extra_members = random.sample(potential_members, 2)
            for member in extra_members:
                if member not in group.members.all():
                    group.members.connect(member)
            group.save()

        # 3. Tworzymy 20 zadań
        # Zadania przydzielane są do losowo wybranej grupy, a następnie losowo do jednego z jej członków.
        priorities = ["low", "medium", "high"]
        statuses = ["pending", "in-progress", "done"]
        for i in range(1, 21):
            task_name = f"task{i}"
            priority = random.choice(priorities)
            status = random.choice(statuses)
            # Ustalmy datę oddania jako dziś + losowa liczba dni (-5 do 10)
            due_in_days = random.randint(-5, 10)
            due_date = date.today() + timedelta(days=due_in_days)
            # Wybieramy losowo grupę
            group_name = random.choice(list(groups.keys()))
            group = groups[group_name]
            # Wybieramy losowo jednego z członków tej grupy
            group_members = list(group.members.all())
            assigned_node = random.choice(group_members)
            task = Task(
                title=task_name,
                description=f"Opis {task_name}",
                priority=priority,
                status=status,
                due_date=due_date
            ).save()
            task.assigned_to.connect(assigned_node)
            group.tasks.connect(task)
            self.stdout.write(f"Utworzono zadanie {task_name} w grupie {group_name} przypisane do {assigned_node.username}.")

        self.stdout.write("Seeding danych zakończony.")