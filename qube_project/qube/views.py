from django.shortcuts import render, redirect
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm, UserChangeForm
)
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

# Neo4j / neomodel importy
from .models import Group, Task, UserNode, MemberRel
from .forms import GroupForm, UserUpdateForm


def main_view(request):
    """Widok strony głównej."""
    return render(request, 'main.html')


# ========== REJESTRACJA ==========
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tworzymy odpowiednika w Neo4j
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
    user_node = UserNode.nodes.get(username=request.user.username)

    # Grupy, w których user_node jest członkiem
    user_groups = []
    for g in Group.nodes:
        if user_node in g.members.all():
            user_groups.append(g)

    # Grupy, w których jest liderem
    user_created_groups = []
    for g in Group.nodes:
        if g.leader.single() == user_node:
            user_created_groups.append(g)

    # Zadania przypisane do użytkownika
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
from .forms import CreateGroupForm  # jeżeli masz taką formę

@login_required
def create_group_view(request):
    if request.method == "POST":
        name = request.POST.get("group_name")
        description = request.POST.get("group_description", "")
        user = UserNode.nodes.get(username=request.user.username)

        group = Group(name=name).save()
        group.leader.connect(user)  # lider to aktualny user

        # Dodajemy członków (np. z listy "members")
        members = request.POST.getlist("members")  # [username1, username2...]
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

    # GET
    all_users = UserNode.nodes.all()
    return render(request, 'dashboard/create_group.html', {'all_users': all_users})


# ========== USTAWIENIA UŻYTKOWNIKA ==========
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

    return render(request, 'dashboard/settings.html', {'user_form': user_form, 'password_form': password_form})


# ========== GRUPA - STRONA SZCZEGÓŁOWA ==========
@login_required
def group_view(request):
    """Poglądowy widok grupy (nieużywany?), do usunięcia lub dostosowania."""
    return render(request, 'group/group.html')


@login_required
def group_detail_view(request, uid):
    """Widok szczegółów grupy."""
    try:
        group = Group.nodes.get(uid=uid)
    except Group.DoesNotExist:
        messages.error(request, "Nie ma takiej grupy.")
        return redirect('dashboard')

    user_node = UserNode.nodes.get(username=request.user.username)
    is_leader = (group.leader.single() == user_node)

    # Członkowie i zadania
    group_members = group.members.all()  # Neo4j set
    all_tasks = group.tasks.all()        # zadania w grupie

    # Dostępni użytkownicy do dodania (tacy, którzy nie są w members)
    all_users = UserNode.nodes.all()
    available_users = [u for u in all_users if u not in group_members]

    # --- Budowa 'user_tasks' (dla wyświetlania w lewej kolumnie) ---
    # Jeżeli lider => user_tasks = all_tasks, wpp. user_tasks = zadania przypisane do user_node
    if is_leader:
        user_tasks = all_tasks
    else:
        user_tasks = []
        for t in all_tasks:
            if user_node in t.assigned_to.all():
                user_tasks.append(t)

    # --- Budowa member_tasks do środkowej kolumny ---
    # Słownik: {username: [lista_zadan]}
    member_tasks = {}
    for m in group_members:
        member_tasks[m.username] = []

    for t in all_tasks:
        for assigned_u in t.assigned_to.all():
            if assigned_u in group_members:
                member_tasks[assigned_u.username].append(t)

    # --- Budowa member_roles do prawej kolumny ---
    # Słownik: {username: rola}
    member_roles = {}
    for m in group_members:
        rel = group.members.relationship(m)  # rel -> MemberRel
        if rel and rel.role:
            member_roles[m.username] = rel.role
        else:
            member_roles[m.username] = ""

    context = {
        'group': group,
        'group_members': group_members,
        'all_tasks': all_tasks,
        'user_tasks': user_tasks,
        'member_tasks': member_tasks,
        'member_roles': member_roles,
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
        new_member_role = request.POST.get('new_member_role')

        try:
            new_member_node = UserNode.nodes.get(username=new_member_username)
        except UserNode.DoesNotExist:
            messages.error(request, f"Użytkownik '{new_member_username}' nie istnieje.")
            return redirect('group_detail', uid=uid)

        # Dodajemy usera do members
        group.members.connect(new_member_node)

        # Ustawiamy rolę w relacji
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

        # Tworzymy obiekt Task w Neo4j
        new_task = Task(title=title, status=status).save()
        # Ewentualnie new_task.description = description / new_task.priority = priority

        # Przypisanie do usera
        try:
            user_for_task = UserNode.nodes.get(username=assigned_user)
            new_task.assigned_to.connect(user_for_task)
        except UserNode.DoesNotExist:
            messages.warning(request, f"Nie znaleziono użytkownika: {assigned_user}")

        # Dodaj zadanie do grupy
        group.tasks.connect(new_task)

        messages.success(request, f"Zadanie '{title}' zostało dodane.")
        return redirect('group_detail', uid=uid)
    else:
        return redirect('group_detail', uid=uid)