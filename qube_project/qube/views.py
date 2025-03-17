from django.shortcuts import render, redirect
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm, UserChangeForm
)
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

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

    # Zadania przypisane do usera
    for t in Task.nodes:
        if user_node in t.assigned_to.all():
            user_tasks.append(t)

    context = {
        'user_groups': user_groups,
        'user_created_groups': user_created_groups,
        'user_tasks': user_tasks,
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
def group_detail_view(request, uid):
    try:
        group = Group.nodes.get(uid=uid)
    except Group.DoesNotExist:
        messages.error(request, "Nie ma takiej grupy.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
    is_leader = (group.leader.single() == user_node)

    group_members = group.members.all()
    all_tasks = group.tasks.all()

    # Pobierz kryteria filtrowania z GET (np. status, priorytet, data)
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    due_date_filter = request.GET.get('due_date')  # np. "2025-03-20"

    # Przefiltruj zadania
    filtered_tasks = []
    for task in all_tasks:
        if status_filter and task.status != status_filter:
            continue
        if priority_filter and task.priority != priority_filter:
            continue
        if due_date_filter:
            try:
                # Zamień podaną datę na obiekt date
                from datetime import datetime
                due_date_crit = datetime.strptime(due_date_filter, "%Y-%m-%d").date()
                if task.due_date and task.due_date != due_date_crit:
                    continue
            except ValueError:
                pass
        filtered_tasks.append(task)

    # Dla członków – filtrowanie tylko ich zadań (jeśli nie lider)
    user_tasks = []
    if not is_leader:
        for t in filtered_tasks:
            if user_node in t.assigned_to.all():
                user_tasks.append(t)

    # Buduj mapę zadań przypisanych do poszczególnych członków
    member_tasks = {}
    for member in group_members:
        member_tasks[member.username] = []
        for t in filtered_tasks:
            if member in t.assigned_to.all():
                member_tasks[member.username].append(t)

    # Lista użytkowników, którzy nie są członkami (do dodawania)
    all_users = UserNode.nodes.all()
    available_users = [u for u in all_users if u not in group_members]

    # Role członków
    member_roles = {}
    for member in group_members:
        rel = group.members.relationship(member)
        if rel and rel.role:
            member_roles[member.username] = rel.role

    context = {
        'group': group,
        'group_members': group_members,
        'all_tasks': filtered_tasks,
        'user_tasks': user_tasks,
        'member_tasks': member_tasks,
        'member_roles': member_roles,
        'is_leader': is_leader,
        'available_users': available_users,
        # przekazujemy też aktualne filtry, żeby formularz mógł je wyświetlać
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'due_date_filter': due_date_filter,
    }
    return render(request, 'group/group_detail.html', context)

@login_required
def add_member_view(request, uid):
    try:
        group = Group.nodes.get(uid=uid)
    except Group.DoesNotExist:
        messages.error(request, "Taka grupa nie istnieje.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
    if group.leader.single() != user_node:
        messages.error(request, "Brak uprawnień do dodawania członków.")
        return redirect('group_detail', uid=uid)

    if request.method == 'POST':
        new_member_username = request.POST.get('new_member_username')
        new_member_role = request.POST.get('new_member_role', "")

        try:
            new_member_node = UserNode.nodes.get(username=new_member_username)
        except UserNode.DoesNotExist:
            messages.error(request, f"Użytkownik '{new_member_username}' nie istnieje.")
            return redirect('group_detail', uid=uid)

        group.members.connect(new_member_node)
        if new_member_role:
            rel = group.members.relationship(new_member_node)
            rel.role = new_member_role
            rel.save()

        messages.success(request, f"Dodano użytkownika '{new_member_username}' z rolą '{new_member_role}'.")
        return redirect('group_detail', uid=uid)
    else:
        return redirect('group_detail', uid=uid)

@login_required
def add_task_view(request, uid):
    try:
        group = Group.nodes.get(uid=uid)
    except Group.DoesNotExist:
        messages.error(request, "Taka grupa nie istnieje.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
    if group.leader.single() != user_node:
        messages.error(request, "Brak uprawnień do dodawania zadań.")
        return redirect('group_detail', uid=uid)

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
        return redirect('group_detail', uid=uid)
    else:
        return redirect('group_detail', uid=uid)