# qube/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from qube.models import Group, Task, UserNode, MemberRel
from datetime import date, timedelta
import random
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = "Wypełnia bazę przykładowymi danymi: 20 użytkowników, 8 grup (3-8 członków) z rolami, 50 zadań (low/medium/high)."

    def handle(self, *args, **options):
        self.stdout.write("Rozpoczynam seeding danych...")

        # 1. Tworzymy 20 użytkowników w Neo4j z polskimi imionami
        user_names = [
            "Anna", "Bartek", "Celina", "Dawid", "Ewa",
            "Filip", "Grażyna", "Hubert", "Iwona", "Julia",
            "Kacper", "Lena", "Michał", "Natalia", "Oskar",
            "Paulina", "Robert", "Sylwia", "Tomasz", "Weronika"
        ]
        users = {}
        for name in user_names:
            username = name
            email = f"{name.lower()}@przyklad.com"
            password = make_password("zaq1@WSX")  # hasło testowe
            try:
                user_node = UserNode.nodes.get(username=username)
                self.stdout.write(f"Użytkownik {username} już istnieje.")
            except UserNode.DoesNotExist:
                user_node = UserNode(username=username, email=email, password=password).save()
                self.stdout.write(f"Utworzono użytkownika {username}.")
            users[username] = user_node

        # 2. Tworzymy 8 grup z polskimi nazwami (3-8 członków w każdej)
        group_names = [
            "Programiści", "Projektanci", "Marketing", "Wsparcie Techniczne",
            "HR", "Sprzedaż", "Finanse", "Badania i Rozwój"
        ]
        groups = {}
        # Zestaw przykładowych ról (oprócz lidera)
        member_roles = ["Developer", "Designer", "Tester", "Scrum Master", "PM"]

        for group_name in group_names:
            # Losujemy liczbę członków od 3 do 8
            num_members = random.randint(3, 8)
            # Wybieramy losowo num_members z listy użytkowników
            members = random.sample(list(users.values()), num_members)
            # Losowo wybieramy lidera spośród wybranych członków
            leader = random.choice(members)
            # Tworzymy grupę
            group = Group(name=group_name).save()
            # Ustawiamy lidera
            group.leader.connect(leader)

            for member in members:
                group.members.connect(member)
                # Jeśli dany member jest liderem – przypisujemy rolę "Leader", w przeciwnym razie losową rolę
                if member == leader:
                    role = "Leader"
                else:
                    role = random.choice(member_roles)
                # Zapisujemy rolę w relacji
                rel = group.members.relationship(member)
                rel.role = role
                rel.save()

            group.save()
            groups[group_name] = group
            self.stdout.write(f"Utworzono grupę '{group_name}' z liderem {leader.username} i {num_members} członkami.")

        # 3. Tworzymy 50 zadań z priorytetami kompatybilnymi z templatkami
        priorities = ["low", "medium", "high"]  # pasują do filtra priority_symbol/priority_color
        statuses = ["oczekujące", "w trakcie", "zakończone"]
        sample_tasks = [
            "Implementacja funkcji logowania",
            "Naprawa błędu płatności",
            "Projektowanie strony głównej",
            "Aktualizacja panelu użytkownika",
            "Optymalizacja zapytań do bazy",
            "Poprawa responsywności mobilnej",
            "Stworzenie kampanii marketingowej",
            "Planowanie premiery produktu",
            "Redesign logo firmy",
            "Napisanie artykułu o SEO",
            "Konfiguracja testów A/B",
            "Przeprojektowanie układu strony",
            "Opracowanie REST API",
            "Badanie opinii użytkowników",
            "Aktualizacja polityki prywatności",
            "Integracja usługi zewnętrznej",
            "Poprawa dostępności strony",
            "Przygotowanie prezentacji inwestorskiej",
            "Projektowanie newslettera",
            "Optymalizacja czasu ładowania",
            "Implementacja systemu rejestracji",
            "Wdrożenie logiki koszyka",
            "Analiza konkurencji",
            "Testowanie aplikacji mobilnej",
            "Szkolenie zespołu",
            "Zarządzanie projektami",
            "Aktualizacja systemu CRM",
            "Optymalizacja SEO",
            "Modernizacja interfejsu użytkownika",
            "Integracja z płatnościami online",
            "Wdrożenie protokołów bezpieczeństwa",
            "Zarządzanie danymi",
            "Projektowanie banerów reklamowych",
            "Analiza danych sprzedażowych",
            "Poprawa doświadczenia użytkownika",
            "Usprawnienie logistyki",
            "Planowanie budżetu",
            "Rozwój aplikacji mobilnej",
            "Monitorowanie serwera",
            "Automatyzacja procesów",
            "Testy obciążeniowe",
            "Analiza ryzyka",
            "Przygotowanie strategii marketingowej",
            "Wdrożenie systemu ERP",
            "Zarządzanie zasobami ludzkimi",
            "Współpraca z partnerami biznesowymi",
            "Usprawnienie obsługi klienta",
            "Analiza trendów rynkowych",
            "Rozwój funkcji e-commerce",
            "Optymalizacja logiki biznesowej"
        ]
        # Jeśli lista ma mniej niż 50 pozycji, można zduplikować niektóre tytuły
        while len(sample_tasks) < 50:
            sample_tasks += sample_tasks  # proste powielenie w razie potrzeby

        for i in range(50):
            task_title = sample_tasks[i]
            priority = random.choice(priorities)
            status = random.choice(statuses)
            # Losowa data oddania: dziś + (od -5 do 20 dni)
            due_in_days = random.randint(-5, 20)
            due_date = date.today() + timedelta(days=due_in_days)
            # Losujemy grupę spośród 8
            group = random.choice(list(groups.values()))
            # Wybieramy losowo jednego z członków tej grupy
            group_members = list(group.members.all())
            assigned_node = random.choice(group_members)

            # Tworzymy zadanie w Neo4j
            task = Task(
                title=task_title,
                description=f"Opis zadania: {task_title}",
                priority=priority,      # "low", "medium", "high"
                status=status,
                due_date=due_date
            ).save()
            # Podłączamy do wybranego użytkownika i grupy
            task.assigned_to.connect(assigned_node)
            group.tasks.connect(task)

            self.stdout.write(
                f"Utworzono zadanie '{task_title}' (priorytet={priority}) w grupie '{group.name}', przypisane do {assigned_node.username}."
            )

        self.stdout.write("Seeding danych zakończony.")