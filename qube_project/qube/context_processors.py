from .auth_utils import get_current_user

def neo4j_user(request):
    user = get_current_user(request)
    # Ustawiamy atrybut is_authenticated, aby szablony mogły sprawdzać ten warunek
    if user:
        user.is_authenticated = True
    return {'user': user}