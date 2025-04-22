from django.shortcuts import render, redirect
from django.contrib import messages
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime

from .models import Group, Task, UserNode, MemberRel
from .forms import (
    Neo4jUserCreationForm,
    Neo4jUserUpdateForm,
    Neo4jPasswordChangeForm,
    CreateGroupForm,
    GroupForm,
    Neo4jLoginForm
)
from .auth_utils import neo4j_login_required, get_current_user
from django.contrib.auth.hashers import check_password, make_password

def main_view(request):
    return render(request, 'main.html')

# ========== REJESTRACJA ==========
def register_view(request):
    if request.method == 'POST':
        form = Neo4jUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Sprawdzamy, czy użytkownik o danej nazwie już istnieje
                UserNode.nodes.get(username=form.cleaned_data['username'])
                messages.error(request, "Użytkownik o podanej nazwie już istnieje.")
            except UserNode.DoesNotExist:
                user = form.save()
                request.session['username'] = user.username
                messages.success(request, "Rejestracja zakończona sukcesem!")
                return redirect('dashboard')
        else:
            messages.error(request, "Błąd w trakcie rejestracji.")
    else:
        form = Neo4jUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

# ========== LOGOWANIE & WYLOGOWANIE ==========
def login_view(request):
    # Inicjalizacja formularza logowania
    form = Neo4jLoginForm()
    if request.method == 'POST':
        form = Neo4jLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = UserNode.nodes.get(username=username)
                if check_password(password, user.password):
                    request.session['username'] = user.username
                    messages.success(request, "Zalogowano pomyślnie!")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Niepoprawne dane logowania.")
            except UserNode.DoesNotExist:
                messages.error(request, "Niepoprawne dane logowania.")
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    request.session.flush()
    messages.info(request, "Wylogowano.")
    return redirect('home')

# ========== DASHBOARD (Neo4j) ==========
@neo4j_login_required
def dashboard_view(request):
    user_node = get_current_user(request)
    if not user_node:
        messages.error(request, "Błąd autoryzacji.")
        return redirect('login')
    
    # Jeśli użytkownik nie istnieje w Neo4j (co zdarza się rzadko), tworzymy go
    try:
        user_node = UserNode.nodes.get(username=user_node.username)
    except UserNode.DoesNotExist:
        user_node = UserNode(username=user_node.username, email=user_node.email).save()
    
    user_groups = []
    user_created_groups = []
    user_tasks = []

    # Grupy, w których użytkownik jest członkiem
    for g in Group.nodes:
        if user_node in g.members.all():
            user_groups.append(g)

    # Grupy, w których użytkownik jest liderem
    for g in Group.nodes:
        if g.leader.single() == user_node:
            user_created_groups.append(g)

    # Łączymy grupy, unikając duplikatów
    user_all_groups = list({g.uid: g for g in user_groups + user_created_groups}.values())

    # Zadania przypisane do użytkownika
    for t in Task.nodes:
        if user_node in t.assigned_to.all():
            user_tasks.append(t)

    task_group_mapping = {}
    for task in user_tasks:
        for group in user_all_groups:
            if task in group.tasks.all():
                task_group_mapping[task.uid] = group.name
                break

    context = {
        'user_groups': user_all_groups,
        'user_created_groups': user_created_groups,
        'user_tasks': user_tasks,
        'task_group_mapping': task_group_mapping,
    }
    return render(request, 'dashboard/dashboard.html', context)

# ========== TWORZENIE GRUPY (Neo4j) ==========
@neo4j_login_required
def create_group_view(request):
    if request.method == "POST":
        name = request.POST.get("group_name")
        description = request.POST.get("group_description", "")
        user = get_current_user(request)

        group = Group(name=name).save()
        group.leader.connect(user)
        group.members.connect(user)

        members = request.POST.getlist("members")
        for username in members:
            try:
                member_node = UserNode.nodes.get(username=username)
                group.members.connect(member_node)
                role_key = f"role_{username}"
                role = request.POST.get(role_key, "")
                if role:
                    rel = group.members.relationship(member_node)
                    rel.role = role
                    rel.save()
            except UserNode.DoesNotExist:
                pass

        messages.success(request, "Grupa została utworzona!")
        return redirect('dashboard')

    # Wykluczamy aktualnie zalogowanego użytkownika
    all_users = [u for u in UserNode.nodes.all() if u.username != get_current_user(request).username]
    return render(request, 'dashboard/create_group.html', {'all_users': all_users})

# ========== USTAWIENIA UŻYTKOWNIKA (zmiana danych i hasła) ==========
@neo4j_login_required
def settings_view(request):
    user = get_current_user(request)
    if request.method == "POST":
        # Rozróżniamy akcję – aktualizacja danych lub zmiana hasła
        if 'update_profile' in request.POST:
            user_form = Neo4jUserUpdateForm(request.POST)
            if user_form.is_valid():
                data = user_form.cleaned_data
                user.first_name = data.get('first_name')
                user.last_name = data.get('last_name')
                user.email = data.get('email')
                user.save()
                messages.success(request, "Dane użytkownika zaktualizowane.")
                return redirect('dashboard')
            else:
                messages.error(request, "Błąd w trakcie aktualizacji danych.")
        elif 'change_password' in request.POST:
            password_form = Neo4jPasswordChangeForm(request.POST)
            if password_form.is_valid():
                if not check_password(password_form.cleaned_data.get('old_password'), user.password):
                    messages.error(request, "Stare hasło jest niepoprawne.")
                else:
                    new_pass = make_password(password_form.cleaned_data.get('new_password1'))
                    user.password = new_pass
                    user.save()
                    messages.success(request, "Hasło zostało zmienione.")
                    return redirect('dashboard')
            else:
                messages.error(request, "Błąd w trakcie zmiany hasła.")
    else:
        user_form = Neo4jUserUpdateForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email
        })
        password_form = Neo4jPasswordChangeForm()
    return render(request, 'dashboard/settings.html', {
        'user_form': user_form,
        'password_form': password_form
    })

# ========== GRUPA - STRONA SZCZEGÓŁOWA ==========
@neo4j_login_required
def group_view(request):
    """Jeśli nie używasz tego widoku, możesz go usunąć."""
    return render(request, 'group/group.html')

@neo4j_login_required
def group_detail_view(request, group_uid):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Nie ma takiej grupy.")
        return redirect('dashboard')

    user_node = get_current_user(request)
    is_leader = (group.leader.single() == user_node)

    # Pobieramy członków grupy jako listę
    group_members = list(group.members.all())
    leader = group.leader.single()
    if leader not in group_members:
        group_members.insert(0, leader)

    all_tasks = group.tasks.all()
    
    # Aktualizacja statusu blokady dla wszystkich zadań w grupie
    for task in all_tasks:
        task.update_blocked_status()

    # Filtrowanie zadań na podstawie parametrów GET (jeśli są)
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    due_date_filter = request.GET.get('due_date')  # oczekiwany format "YYYY-MM-DD"
    blocked_filter = request.GET.get('blocked')

    # Pobierz listę ukończonych zadań dla modalu
    completed_tasks = [task for task in all_tasks if task.status == "Zakończone"]
    
    filtered_tasks = []
    for task in all_tasks:
        if status_filter and task.status != status_filter:
            continue
        if priority_filter and task.priority != priority_filter:
            continue
        if due_date_filter:
            try:
                due_date_crit = datetime.strptime(due_date_filter, "%Y-%m-%d").date()
                if task.due_date and task.due_date != due_date_crit:
                    continue
            except ValueError:
                pass
        if blocked_filter:
            if blocked_filter == "true" and not task.is_blocked:
                continue
            if blocked_filter == "false" and task.is_blocked:
                continue
        filtered_tasks.append(task)

    # Jeśli użytkownik nie jest liderem, pokaż tylko zadania do których jest przypisany
    user_tasks = []
    if not is_leader:
        for t in filtered_tasks:
            if user_node in t.assigned_to.all():
                user_tasks.append(t)

    # Budowanie mapy zadań przypisanych do poszczególnych członków
    member_tasks = {}
    for member in group_members:
        member_tasks[member.username] = []
        for t in filtered_tasks:
            if member in t.assigned_to.all():
                member_tasks[member.username].append(t)

    all_users = UserNode.nodes.all()
    available_users = [u for u in all_users if u not in group_members]

    member_roles = {}
    for member in group_members:
        rel = group.members.relationship(member)
        if rel and rel.role:
            member_roles[member.username] = rel.role

    # Przygotowanie danych o zależnościach dla każdego zadania
    task_dependencies = {}
    for task in all_tasks:
        task_dependencies[task.uid] = list(task.depends_on.all())

    context = {
        'group': group,
        'leader': leader,
        'group_members': group_members,
        'all_tasks': filtered_tasks,
        'user_tasks': user_tasks,
        'member_tasks': member_tasks,
        'member_roles': member_roles,
        'is_leader': is_leader,
        'available_users': available_users,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'due_date_filter': due_date_filter,
        'task_dependencies': task_dependencies,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'group/group_detail.html', context)

@neo4j_login_required
def add_member_view(request, group_uid):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Taka grupa nie istnieje.")
        return redirect('dashboard')

    user_node = get_current_user(request)
    if group.leader.single() != user_node:
        messages.error(request, "Brak uprawnień do dodawania członków.")
        return redirect('group_detail', group_uid=group_uid)

    if request.method == 'POST':
        new_member_username = request.POST.get('new_member_username')
        new_member_role = request.POST.get('new_member_role', "")

        try:
            new_member_node = UserNode.nodes.get(username=new_member_username)
        except UserNode.DoesNotExist:
            messages.error(request, f"Użytkownik '{new_member_username}' nie istnieje.")
            return redirect('group_detail', group_uid=group_uid)

        group.members.connect(new_member_node)
        if new_member_role:
            rel = group.members.relationship(new_member_node)
            rel.role = new_member_role
            rel.save()

        messages.success(request, f"Dodano użytkownika '{new_member_username}' z rolą '{new_member_role}'.")
        return redirect('group_detail', group_uid=group_uid)
    else:
        return redirect('group_detail', group_uid=group_uid)

@neo4j_login_required
def add_task_view(request, group_uid):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Taka grupa nie istnieje.")
        return redirect('dashboard')

    user_node = get_current_user(request)
    if group.leader.single() != user_node:
        messages.error(request, "Brak uprawnień do dodawania zadań.")
        return redirect('group_detail', group_uid=group_uid)

    if request.method == 'POST':
        title = request.POST.get('title')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        description = request.POST.get('description')
        due_date_str = request.POST.get('due_date')  # data w formacie "YYYY-MM-DD"

        # Tworzenie nowego zadania
        new_task = Task(
            title=title,
            status=status,
            priority=priority,
            description=description
        ).save()

        if due_date_str:
            try:
                new_task.due_date = date.fromisoformat(due_date_str)
                new_task.save()
            except ValueError:
                messages.warning(request, f"Nieprawidłowy format daty: {due_date_str}")

        # Przypisywanie użytkowników (obsługa wielu użytkowników)
        assigned_users = request.POST.getlist('assigned_user')
        for username in assigned_users:
            try:
                user_for_task = UserNode.nodes.get(username=username)
                new_task.assigned_to.connect(user_for_task)
            except UserNode.DoesNotExist:
                messages.warning(request, f"Nie znaleziono użytkownika: {username}")

        # Dodawanie zależności zadań
        dependency_tasks = request.POST.getlist('dependency_tasks')
        has_dependencies = False
        for task_uid in dependency_tasks:
            try:
                dependency_task = Task.nodes.get(uid=task_uid)
                new_task.depends_on.connect(dependency_task)
                has_dependencies = True
            except Task.DoesNotExist:
                messages.warning(request, f"Nie znaleziono zadania o ID: {task_uid}")

        # Jeśli zadanie ma zależności, sprawdzamy jego status blokady
        if has_dependencies:
            new_task.update_blocked_status()

        # Łączenie zadania z grupą
        group.tasks.connect(new_task)

        messages.success(request, f"Zadanie '{title}' zostało dodane.")
        return redirect('group_detail', group_uid=group_uid)
    else:
        return redirect('group_detail', group_uid=group_uid)
    
@neo4j_login_required
def edit_task_view(request, group_uid, task_uid):
    try:
        task = Task.nodes.get(uid=task_uid)
    except Task.DoesNotExist:
        messages.error(request, "Zadanie nie istnieje.")
        return redirect('dashboard')
    
    group = None
    for g in Group.nodes:
        if task in g.tasks.all():
            group = g
            break
    if not group:
        messages.error(request, "Nie można znaleźć grupy dla tego zadania.")
        return redirect('dashboard')

    user_node = get_current_user(request)
    is_leader = (group.leader.single() == user_node)
    if not (is_leader or (user_node in task.assigned_to.all())):
        messages.error(request, "Brak uprawnień do edycji zadania.")
        return redirect('group_detail', group_uid=group.uid)

    # Pobieramy przypisanych użytkowników
    assigned_users = list(task.assigned_to.all())
    # Pobieramy zależności zadania
    dependencies = list(task.depends_on.all())

    if request.method == "POST":
        old_status = task.status
        new_status = request.POST.get('status')
        
        if is_leader:
            task.title = request.POST.get('title')
            task.priority = request.POST.get('priority')
            due_date = request.POST.get('due_date')
            if due_date:
                try:
                    task.due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                except ValueError:
                    task.due_date = None
            else:
                task.due_date = None

            # Aktualizacja przypisanych użytkowników
            task.assigned_to.disconnect_all()
            assigned_users = request.POST.getlist('assigned_user')
            for username in assigned_users:
                try:
                    user = UserNode.nodes.get(username=username)
                    task.assigned_to.connect(user)
                except UserNode.DoesNotExist:
                    messages.warning(request, f"Użytkownik {username} nie istnieje.")
            
            # Aktualizacja zależności zadań
            task.depends_on.disconnect_all()
            dependency_tasks = request.POST.getlist('dependency_tasks')
            for dep_uid in dependency_tasks:
                try:
                    dep_task = Task.nodes.get(uid=dep_uid)
                    task.depends_on.connect(dep_task)
                except Task.DoesNotExist:
                    messages.warning(request, f"Zadanie zależne o ID {dep_uid} nie istnieje.")
        
        task.description = request.POST.get('description')
        task.status = new_status
        
        # Aktualizacja daty ukończenia, jeśli status się zmienił na "Zakończone"
        if old_status != "Zakończone" and new_status == "Zakończone":
            task.completion_date = date.today()
        # Usunięcie daty ukończenia, jeśli status się zmienił z "Zakończone" na inny
        elif old_status == "Zakończone" and new_status != "Zakończone":
            task.completion_date = None
            
        # Aktualizacja statusu blokady
        task.update_blocked_status()
        task.save()
        
        messages.success(request, "Zadanie zostało zaktualizowane.")
        return redirect('group_detail', group_uid=group.uid)
    else:
        # Pobieramy wszystkie zadania w grupie oprócz edytowanego
        all_tasks = [t for t in group.tasks.all() if t.uid != task.uid]
        
        context = {
            'task': task,
            'group': group,
            'group_members': group.members.all(),
            'is_leader': is_leader,
            'assigned_users': assigned_users,
            'all_tasks': all_tasks,
            'dependencies': dependencies
        }
        return render(request, 'group/edit_task.html', context)
    
@neo4j_login_required
def edit_member_view(request, group_uid, username):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Grupa nie istnieje.")
        return redirect('dashboard')
    user_node = get_current_user(request)
    is_leader = (group.leader.single() == user_node)
    if not is_leader:
        messages.error(request, "Brak uprawnień do edycji członków grupy.")
        return redirect('group_detail', group_uid=group.uid)
    try:
        member = UserNode.nodes.get(username=username)
    except UserNode.DoesNotExist:
        messages.error(request, "Użytkownik nie istnieje.")
        return redirect('group_detail', group_uid=group.uid)
    
    if request.method == "POST":
        if request.POST.get('delete') == "1":
            if request.POST.get('delete_tasks') == "1":
                tasks_to_delete = [task for task in group.tasks.all() if member in task.assigned_to.all()]
                for task in tasks_to_delete:
                    group.tasks.disconnect(task)
                    task.delete()
                group.save()
            else:
                for task in group.tasks.all():
                    if member in task.assigned_to.all():
                        task.assigned_to.disconnect(member)
            group.members.disconnect(member)
            messages.success(request, f"Użytkownik {username} został usunięty z grupy.")
        else:
            new_role = request.POST.get('role')
            rel = group.members.relationship(member)
            if new_role:
                rel.role = new_role
                rel.save()
                messages.success(request, f"Rola użytkownika {username} została zaktualizowana.")
            else:
                messages.error(request, "Nie podano roli. Aby usunąć członka, użyj przycisku 'Usuń członka'.")
        return redirect('group_detail', group_uid=group.uid)
    else:
        current_role = ""
        rel = group.members.relationship(member)
        if rel and rel.role:
            current_role = rel.role
        context = {
            'group': group,
            'member': member,
            'current_role': current_role,
        }
        return render(request, 'group/edit_member.html', context)

@neo4j_login_required
@require_POST
def update_group_name_view(request, uid):
    try:
        group = Group.nodes.get(uid=uid)
    except Group.DoesNotExist:
        return JsonResponse({"success": False, "error": "Grupa nie istnieje."})
    
    user_node = get_current_user(request)
    if group.leader.single() != user_node:
        return JsonResponse({"success": False, "error": "Brak uprawnień."})
    
    try:
        data = json.loads(request.body)
        new_name = data.get("name")
        if new_name:
            group.name = new_name
            group.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Brak nowej nazwy."})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
    
@neo4j_login_required
@require_POST
def delete_group_view(request, group_uid):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Grupa nie istnieje.")
        return redirect('dashboard')

    user_node = get_current_user(request)
    if group.leader.single() != user_node:
        messages.error(request, "Brak uprawnień do usunięcia grupy.")
        return redirect('group_detail', group_uid=group_uid)

    tasks_in_group = group.tasks.all()
    for task in tasks_in_group:
        task.delete()

    group.delete()

    messages.success(request, "Grupa oraz wszystkie jej zadania zostały usunięte.")
    return redirect('dashboard')

@neo4j_login_required
def delete_completed_tasks_view(request, group_uid):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Grupa nie istnieje.")
        return redirect('dashboard')

    user_node = get_current_user(request)
    is_leader = (group.leader.single() == user_node)
    
    # Tylko lider grupy może usuwać zadania
    if not is_leader:
        messages.error(request, "Brak uprawnień do usuwania zadań.")
        return redirect('group_detail', group_uid=group_uid)

    if request.method == "POST":
        delete_all = request.POST.get('delete_all') == '1'
        
        if delete_all:
            # Usuwanie wszystkich ukończonych zadań
            tasks_to_delete = []
            for task in group.tasks.all():
                if task.status == "Zakończone":
                    tasks_to_delete.append(task)
            
            for task in tasks_to_delete:
                group.tasks.disconnect(task)
                task.delete()
            
            messages.success(request, f"Usunięto wszystkie ukończone zadania ({len(tasks_to_delete)}).")
        else:
            # Usuwanie wybranych zadań
            selected_tasks = request.POST.getlist('selected_tasks')
            deleted_count = 0
            
            for task_uid in selected_tasks:
                try:
                    task = Task.nodes.get(uid=task_uid)
                    if task in group.tasks.all() and task.status == "Zakończone":
                        group.tasks.disconnect(task)
                        task.delete()
                        deleted_count += 1
                except Task.DoesNotExist:
                    continue
            
            if deleted_count > 0:
                messages.success(request, f"Usunięto {deleted_count} zadań.")
            else:
                messages.info(request, "Nie wybrano żadnych zadań do usunięcia.")
    
    return redirect('group_detail', group_uid=group_uid)

@neo4j_login_required
def delete_task_view(request, group_uid, task_uid):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Grupa nie istnieje.")
        return redirect('dashboard')

    user_node = get_current_user(request)
    is_leader = (group.leader.single() == user_node)
    
    # Tylko lider grupy może usuwać zadania
    if not is_leader:
        messages.error(request, "Brak uprawnień do usuwania zadań.")
        return redirect('group_detail', group_uid=group_uid)

    try:
        task = Task.nodes.get(uid=task_uid)
    except Task.DoesNotExist:
        messages.error(request, "Zadanie nie istnieje.")
        return redirect('group_detail', group_uid=group_uid)

    # Sprawdź, czy zadanie należy do tej grupy
    if task not in group.tasks.all():
        messages.error(request, "Zadanie nie należy do tej grupy.")
        return redirect('group_detail', group_uid=group_uid)

    if request.method == "POST":
        # Najpierw zaktualizuj wszystkie zadania, które zależą od tego
        dependent_tasks = []
        for t in group.tasks.all():
            if task in t.depends_on.all():
                dependent_tasks.append(t)
        
        # Usuń to zadanie z zależności innych zadań
        for dep_task in dependent_tasks:
            dep_task.depends_on.disconnect(task)
            dep_task.update_blocked_status()
        
        # Usuń zadanie
        task_title = task.title
        group.tasks.disconnect(task)
        task.delete()
        
        messages.success(request, f"Zadanie '{task_title}' zostało usunięte.")
        return redirect('group_detail', group_uid=group_uid)
    
    return redirect('group_detail', group_uid=group_uid)