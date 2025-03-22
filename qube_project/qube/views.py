from django.shortcuts import render, redirect
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm, UserChangeForm
)
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Group, Task, UserNode, MemberRel
from .forms import GroupForm, UserUpdateForm, CreateGroupForm

from datetime import date, datetime

def main_view(request):
    return render(request, 'main.html')

# ========== REJESTRACJA ==========
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tworzymy węzeł Neo4j
            UserNode(username=user.username, email=user.email).save()
            auth_login(request, user)
            messages.success(request, "Rejestracja zakończona sukcesem!")
            return redirect('dashboard')
        else:
            messages.error(request, "Błąd w trakcie rejestracji.")
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

# ========== LOGOWANIE & WYLOGOWANIE ==========
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "Zalogowano pomyślnie!")
            return redirect('dashboard')
        else:
            messages.error(request, "Niepoprawne dane logowania.")
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Wylogowano.")
    return redirect('home')

# ========== DASHBOARD (Neo4j) ==========
@login_required
def dashboard_view(request):
    user_node = UserNode.nodes.get(username=request.user.username)
    user_groups = []
    user_created_groups = []
    user_tasks = []

    # Grupy, w których user jest członkiem
    for g in Group.nodes:
        if user_node in g.members.all():
            user_groups.append(g)

    # Grupy, w których jest liderem
    for g in Group.nodes:
        if g.leader.single() == user_node:
            user_created_groups.append(g)

    # Połącz listy, unikając duplikatów (np. gdy lider nie jest automatycznie członkiem)
    user_all_groups = list({g.uid: g for g in user_groups + user_created_groups}.values())

    # Zadania przypisane do usera
    for t in Task.nodes:
        if user_node in t.assigned_to.all():
            user_tasks.append(t)

    # Dla każdego zadania znajdź pierwszą grupę, w której się znajduje
    task_group_mapping = {}
    for task in user_tasks:
        for group in user_all_groups:
            if task in group.tasks.all():
                task_group_mapping[task.uid] = group.name
                break  # Break jest już w Pythonie, tutaj to działa

    context = {
        'user_groups': user_all_groups,  # wszystkie grupy użytkownika
        'user_created_groups': user_created_groups,  # lista grup, w których użytkownik jest liderem
        'user_tasks': user_tasks,
        'task_group_mapping': task_group_mapping,
    }
    return render(request, 'dashboard/dashboard.html', context)

# ========== TWORZENIE GRUPY (Neo4j) ==========
@login_required
def create_group_view(request):
    if request.method == "POST":
        name = request.POST.get("group_name")
        description = request.POST.get("group_description", "")
        user = UserNode.nodes.get(username=request.user.username)

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

    all_users = UserNode.nodes.all()
    return render(request, 'dashboard/create_group.html', {'all_users': all_users})

# ========== USTAWIENIA UŻYTKOWNIKA (zmiana danych i hasła) ==========
@login_required
def settings_view(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, "Dane użytkownika zaktualizowane.")
            return redirect('dashboard')

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Hasło zostało zmienione.")
            return redirect('dashboard')

        messages.error(request, "Błąd w trakcie aktualizacji ustawień.")

    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'dashboard/settings.html', {
        'user_form': user_form,
        'password_form': password_form
    })

# ========== GRUPA - STRONA SZCZEGÓŁOWA ==========

@login_required
def group_view(request):
    """Jeśli nie używasz tego widoku, możesz go usunąć."""
    return render(request, 'group/group.html')

@login_required
def group_detail_view(request, group_uid):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Nie ma takiej grupy.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
    is_leader = (group.leader.single() == user_node)

    # Pobierz członków grupy jako listę
    group_members = list(group.members.all())
    leader = group.leader.single()
    # Upewnij się, że lider jest na liście (jeśli nie, dodaj go na początek)
    if leader not in group_members:
        group_members.insert(0, leader)

    all_tasks = group.tasks.all()

    # Filtrowanie zadań na podstawie parametrów GET (jeśli są)
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    due_date_filter = request.GET.get('due_date')  # oczekiwany format "YYYY-MM-DD"

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
        filtered_tasks.append(task)

    # Jeśli user nie jest liderem, pokaż tylko jego zadania
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
    }
    return render(request, 'group/group_detail.html', context)

@login_required
def add_member_view(request, group_uid):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Taka grupa nie istnieje.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
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

@login_required
def add_task_view(request, group_uid):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Taka grupa nie istnieje.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
    if group.leader.single() != user_node:
        messages.error(request, "Brak uprawnień do dodawania zadań.")
        return redirect('group_detail', group_uid=group_uid)

    if request.method == 'POST':
        title = request.POST.get('title')
        assigned_user = request.POST.get('assigned_user')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        description = request.POST.get('description')
        due_date_str = request.POST.get('due_date')  # data w formacie "YYYY-MM-DD"

        # Tworzymy i zapisujemy obiekt Task
        new_task = Task(
            title=title,
            status=status,
            priority=priority,
            description=description
        ).save()

        # Ustawiamy due_date (jeśli podano)
        if due_date_str:
            from datetime import date
            try:
                new_task.due_date = date.fromisoformat(due_date_str)
                new_task.save()
            except ValueError:
                messages.warning(request, f"Nieprawidłowy format daty: {due_date_str}")

        # Łączymy zadanie z userem
        try:
            user_for_task = UserNode.nodes.get(username=assigned_user)
            new_task.assigned_to.connect(user_for_task)
        except UserNode.DoesNotExist:
            messages.warning(request, f"Nie znaleziono użytkownika: {assigned_user}")

        # Łączymy zadanie z grupą
        group.tasks.connect(new_task)

        messages.success(request, f"Zadanie '{title}' zostało dodane.")
        return redirect('group_detail', group_uid=group_uid)
    else:
        return redirect('group_detail', group_uid=group_uid)
    
@login_required
def edit_task_view(request, group_uid, task_uid):
    try:
        task = Task.nodes.get(uid=task_uid)
    except Task.DoesNotExist:
        messages.error(request, "Zadanie nie istnieje.")
        return redirect('dashboard')
    
    # Znajdź grupę, do której należy zadanie (zakładamy, że zadanie należy do jednej grupy)
    group = None
    for g in Group.nodes:
        if task in g.tasks.all():
            group = g
            break
    if not group:
        messages.error(request, "Nie można znaleźć grupy dla tego zadania.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
    is_leader = (group.leader.single() == user_node)
    # Użytkownik może edytować zadanie, jeśli jest liderem lub jest przypisany do zadania
    if not (is_leader or (user_node in task.assigned_to.all())):
        messages.error(request, "Brak uprawnień do edycji zadania.")
        return redirect('group_detail', group_uid=group.uid)

    if request.method == "POST":
        # Jeśli użytkownik jest liderem, aktualizujemy wszystkie pola
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

            # Aktualizacja pola assigned_user – najpierw odłączamy, potem łączymy
            task.assigned_to.disconnect_all()
            assigned_username = request.POST.get('assigned_user')
            try:
                assigned_user = UserNode.nodes.get(username=assigned_username)
                task.assigned_to.connect(assigned_user)
            except UserNode.DoesNotExist:
                messages.warning(request, f"Użytkownik {assigned_username} nie istnieje.")
        # Pola wspólne dla obu: opis i status
        task.description = request.POST.get('description')
        task.status = request.POST.get('status')
        task.save()
        messages.success(request, "Zadanie zostało zaktualizowane.")
        return redirect('group_detail', group_uid=group.uid)
    else:
        group_members = group.members.all()
        context = {
            'task': task,
            'group': group,
            'group_members': group_members,
            'is_leader': is_leader,
        }
        return render(request, 'group/edit_task.html', context)


@login_required
def edit_member_view(request, group_uid, username):
    try:
        group = Group.nodes.get(uid=group_uid)
    except Group.DoesNotExist:
        messages.error(request, "Grupa nie istnieje.")
        return redirect('dashboard')
    user_node = UserNode.nodes.get(username=request.user.username)
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
    

@login_required
@require_POST
def update_group_name_view(request, uid):
    try:
        group = Group.nodes.get(uid=uid)
    except Group.DoesNotExist:
        return JsonResponse({"success": False, "error": "Grupa nie istnieje."})
    
    user_node = UserNode.nodes.get(username=request.user.username)
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