from django.shortcuts import render, redirect
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm, UserChangeForm
)
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .models import Group, Task, UserNode  # ✅ Teraz tylko Neo4j!
from .forms import GroupForm, UserUpdateForm


def main_view(request):
    return render(request, 'main.html')


# ========== REJESTRACJA ==========
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserNode(username=user.username, email=user.email).save()  # ✅ Tworzenie użytkownika w Neo4j
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

    # Grupy użytkownika (iteracja, żeby sprawdzić, czy user_node jest w members)
    user_groups = [g for g in Group.nodes if user_node in g.members.all()]

    # Grupy, w których jest liderem
    user_created_groups = [g for g in Group.nodes if g.leader.single() == user_node]

    # Zadania przypisane do użytkownika
    user_tasks = [t for t in Task.nodes if user_node in t.assigned_to.all()]

    context = {
        'user_groups': user_groups,
        'user_created_groups': user_created_groups,
        'user_tasks': user_tasks,
    }
    return render(request, 'dashboard/dashboard.html', context)



# ========== TWORZENIE GRUPY (Neo4j) ==========
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Group, UserNode, MemberRel
from .forms import CreateGroupForm

@login_required
def create_group_view(request):
    if request.method == "POST":
        name = request.POST.get("group_name")
        description = request.POST.get("group_description", "")
        user = UserNode.nodes.get(username=request.user.username)

        # Tworzymy węzeł Group w Neo4j
        group = Group(name=name).save()
        group.leader.connect(user)  # lider to aktualny user
        # Ewentualnie można zapisać opis, jeśli dodasz "description" w modelu

        # Dodajemy członków
        members = request.POST.getlist("members")  # lista username
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

    # GET request
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
    return render(request, 'group/group.html')


@login_required
def group_detail_view(request, uid):
    try:
        group = Group.nodes.get(uid=uid)  # Pobieramy obiekt Group po uid
    except Group.DoesNotExist:
        messages.error(request, "Taka grupa nie istnieje.")
        return redirect('dashboard')

    return render(request, 'group/group_detail.html', {'group': group})

