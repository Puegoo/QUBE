from django.shortcuts import render, redirect
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm, UserChangeForm
)
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

# Importy z Twoich modeli i formularzy (Neo4j)
from .models import Group, Task, UserNode, MemberRel
from .forms import GroupForm, UserUpdateForm, CreateGroupForm

def main_view(request):
    return render(request, 'main.html')

# ========== REJESTRACJA ==========
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tworzymy UserNode w Neo4j
            UserNode(username=user.username, email=user.email).save()
            auth_login(request, user)
            messages.success(request, "Rejestracja zakończona sukcesem!")
            return redirect('dashboard')
        else:
            messages.error(request, "Wystąpił błąd w trakcie rejestracji.")
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
    """Widok głównego panelu (Dashboard)."""
    user_node = UserNode.nodes.get(username=request.user.username)

    # Grupy, w których user jest członkiem
    user_groups = []
    for g in Group.nodes:
        if user_node in g.members.all():
            user_groups.append(g)

    # Grupy, w których jest liderem
    user_created_groups = []
    for g in Group.nodes:
        if g.leader.single() == user_node:
            user_created_groups.append(g)

    # Zadania przypisane do usera
    user_tasks = []
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

        # Tworzymy obiekt Group w Neo4j
        group = Group(name=name).save()
        group.leader.connect(user)  # lider to aktualny user
        # ewentualne zapisy opisu "description" – w modelu

        # Dodajemy członków z listy "members"
        members = request.POST.getlist("members")  # <input name="members" multiple ...>
        for username in members:
            try:
                member_node = UserNode.nodes.get(username=username)
                group.members.connect(member_node)
                # rola:
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

        messages.error(request, "Wystąpił błąd podczas aktualizacji ustawień.")

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
    """Widok szczegółowy grupy: zadania, członkowie, role, itp."""
    try:
        group = Group.nodes.get(uid=uid)
    except Group.DoesNotExist:
        messages.error(request, "Nie ma takiej grupy.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
    is_leader = (group.leader.single() == user_node)

    # Członkowie grupy
    group_members = group.members.all()
    # Zadania w grupie
    all_tasks = group.tasks.all()

    # Lista użytkowników spoza grupy (do <select> przy dodawaniu członka)
    all_users = UserNode.nodes.all()
    available_users = [u for u in all_users if u not in group_members]

    # ============== user_tasks (lewa kolumna) =============
    # jeśli lider => widzi all_tasks, wpp. tylko swoje
    if is_leader:
        user_tasks = all_tasks
    else:
        user_tasks = []
        for t in all_tasks:
            if user_node in t.assigned_to.all():
                user_tasks.append(t)

    # ============== member_tasks (środkowa kolumna) =============
    # Słownik: { username: [zadania przypisane] }
    member_tasks = {}
    for m in group_members:
        member_tasks[m.username] = []

    for t in all_tasks:
        assigned_list = t.assigned_to.all()
        for assigned_user in assigned_list:
            if assigned_user in group_members:
                member_tasks[assigned_user.username].append(t)

    # ============== member_roles (prawa kolumna) =============
    # Słownik: { username: rola }
    member_roles = {}
    for m in group_members:
        rel = group.members.relationship(m)
        if rel and rel.role:
            member_roles[m.username] = rel.role
        else:
            member_roles[m.username] = ""

    context = {
        'group': group,
        'group_members': group_members,
        'all_tasks': all_tasks,      # pełna lista zadań
        'user_tasks': user_tasks,    # zadania dla lewego panelu
        'member_tasks': member_tasks,# zadania dla kolumny środkowej
        'member_roles': member_roles,# role do prawej kolumny
        'is_leader': is_leader,
        'available_users': available_users,
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
    is_leader = (group.leader.single() == user_node)
    if not is_leader:
        messages.error(request, "Nie masz uprawnień do dodawania członków w tej grupie.")
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
        # GET
        return redirect('group_detail', uid=uid)

@login_required
def add_task_view(request, uid):
    try:
        group = Group.nodes.get(uid=uid)
    except Group.DoesNotExist:
        messages.error(request, "Taka grupa nie istnieje.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
    is_leader = (group.leader.single() == user_node)
    if not is_leader:
        messages.error(request, "Nie masz uprawnień do dodawania zadań w tej grupie.")
        return redirect('group_detail', uid=uid)

    if request.method == 'POST':
        title = request.POST.get('title')
        assigned_user = request.POST.get('assigned_user')
        status = request.POST.get('status')
        priority = request.POST.get('priority')
        description = request.POST.get('description')

        new_task = Task(title=title, status=status).save()
        # ewentualnie new_task.description = description, new_task.priority = priority

        try:
            user_for_task = UserNode.nodes.get(username=assigned_user)
            new_task.assigned_to.connect(user_for_task)
        except UserNode.DoesNotExist:
            messages.warning(request, f"Nie znaleziono użytkownika: {assigned_user}")

        group.tasks.connect(new_task)

        messages.success(request, f"Zadanie '{title}' zostało dodane.")
        return redirect('group_detail', uid=uid)
    else:
        return redirect('group_detail', uid=uid)