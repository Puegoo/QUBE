from django import forms
from django.contrib.auth.models import User
from .models import Group
from .models import UserNode

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User  # ✅ Django zarządza użytkownikami
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

# ✅ Grupa w Neo4j – musimy użyć zwykłego `Form`, nie `ModelForm`
class GroupForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwa grupy'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Opis grupy', 'rows': 3}))


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
    # Pole wielokrotnego wyboru userów – wyświetlamy username z bazy
    users = forms.MultipleChoiceField(
        label="Użytkownicy do dodania",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )
    # Pole do wpisywania ról w formacie user:rola, user:rola... (dla uproszczenia)
    roles = forms.CharField(
        required=False,
        label="Role (opcjonalnie)",
        help_text="Format: username1:rola1, username2:rola2",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pobierz wszystkich UserNode
        user_nodes = UserNode.nodes.all()
        # Zbuduj listę krotek (value, label)
        choices = []
        for user_node in user_nodes:
            choices.append((user_node.username, user_node.username))
        self.fields['users'].choices = choices

