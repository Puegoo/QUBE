from django import forms
from django.contrib.auth.hashers import make_password, check_password
from .models import UserNode, Group

# Formularze dotyczące użytkowników (Neo4j)
class Neo4jUserCreationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwa użytkownika'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Hasło'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Powtórz hasło'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Hasła muszą być identyczne.")
        return cleaned_data

    def save(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = make_password(self.cleaned_data['password1'])
        user = UserNode(username=username, email=email, password=password).save()
        return user
    
class Neo4jLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwa użytkownika'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Hasło'})
    )

class Neo4jUserUpdateForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imię'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwisko'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )

class Neo4jPasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Stare hasło'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nowe hasło'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Powtórz nowe hasło'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Nowe hasła muszą być identyczne.")
        return cleaned_data

# Formularze dotyczące grup (Neo4j)
class GroupForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwa grupy'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Opis grupy', 'rows': 3})
    )

class CreateGroupForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Nazwa grupy",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        required=False,
        label="Opis grupy",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    # Pole wyboru użytkowników do dodania
    users = forms.MultipleChoiceField(
        label="Użytkownicy do dodania",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )
    # Pole do wpisywania ról w formacie user:rola, user:rola...
    roles = forms.CharField(
        required=False,
        label="Role (opcjonalnie)",
        help_text="Format: username1:rola1, username2:rola2",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_nodes = UserNode.nodes.all()
        choices = []
        for user_node in user_nodes:
            choices.append((user_node.username, user_node.username))
        self.fields['users'].choices = choices