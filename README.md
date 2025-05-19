<h1 align="center">QUBE</h1>
<div align="center">
  <img src="Docs/images/QUBE_banner.png" width="100%" alt="Baner">
</div>

## Spis treści
1. [Wprowadzenie](#wprowadzenie)
2. [Instalacja](#instalacja)
3. [Struktura projektu](#struktura-projektu)
4. [Funkcjonalności](#funkcjonalności)
5. [Technologie](#technologie)
6. [Architektura](#architektura)
7. [Przyszły rozwój](#przyszły-rozwój)
8. [Galeria](#galeria)
9. [Autorzy](#autorzy)

## Wprowadzenie

<img src="qube_project/qube/static/images/QUBE_LOGO.png" alt="QUBE Logo" align="right" width="200" height="200" />

QUBE to nowoczesna aplikacja webowa do zarządzania projektami i zespołami, wykorzystująca bazę danych grafową Neo4j. Dzięki tej architekturze aplikacja oferuje wydajne zarządzanie złożonymi relacjami między użytkownikami, grupami i zadaniami bez konieczności używania tradycyjnych relacyjnych baz danych.

QUBE umożliwia tworzenie grup projektowych, zarządzanie członkami zespołu z różnymi rolami, przydzielanie i śledzenie zadań oraz monitorowanie postępów. Intuicyjny interfejs użytkownika oparty na Django i czystym JavaScript zapewnia płynne doświadczenie przy korzystaniu z aplikacji.

Projekt został zaprojektowany z myślą o prostocie wdrożenia i użytkowania, eliminując typowe problemy związane z konfiguracją baz danych SQL i kompleksowymi systemami autoryzacji.

## Instalacja

Aby uruchomić projekt, wykonaj następujące kroki:

1. Sklonuj repozytorium: `git clone https://github.com/username/qube.git`
2. Zainstaluj wymagane pakiety Pythona: `pip install -r requirements.txt`
3. Zainstaluj bazę danych [Neo4j](https://neo4j.com/download/) i uruchom ją.
4. W pliku konfiguracyjnym Neo4j ustaw wartość `dbms.security.auth_enabled` na `false`, lub skonfiguruj dane dostępowe w `settings.py`.
5. Uruchom plik `run_project.bat` (dla systemu Windows) lub `run_project.sh` (dla systemów macOS i Linux).

Po wykonaniu tych czynności projekt samoczynnie skonfiguruje bazę i załaduje do niej niezbędne dane.

### Konfiguracja Neo4j

W pliku `settings.py` możesz dostosować konfigurację połączenia Neo4j:

```python
NEOMODEL_NEO4J_BOLT_URL = "bolt://neo4j:qube12345@localhost:7687"
NEOMODEL_SIGNALS = False
NEOMODEL_ENCRYPTED_CONNECTION = False
```

## Struktura projektu
Poniżej przedstawiono przykładową strukturę katalogu głównego projektu:

```
.
├── manage.py                 
├── 📁 qube                   
│   ├── apps.py              
│   ├── auth_utils.py        
│   ├── context_processors.py
│   ├── forms.py             
│   ├── 📁 management        
│   │   └── 📁 commands
│   │       └── seed_data.py          
│   ├── models.py            
│   ├── 📁 static            
│   │   ├── 📁 css           
│   │   ├── 📁 icons         
│   │   ├── 📁 images        
│   │   └── 📁 js            
│   ├── 📁 templates         
│   │   ├── 📁 auth
│   │   │   ├── login.html
│   │   │   └── register.html          
│   │   ├── 📁 dashboard
│   │   │   ├── create_group.html
│   │   │   ├── dashboard.html
│   │   │   └── settings.html     
│   │   ├── 📁 errors
│   │   │   └── 500.html        
│   │   ├── 📁 group 
│   │   │   ├── edit_member.html
│   │   │   ├── edit_task.html
│   │   │   └── group_detail.html        
│   │   ├── main.html        
│   │   └── master.html      
│   ├── 📁 templatetags      
│   │   ├── arithmetic.py    
│   │   └── dict_extras.py   
│   ├── tests.py             
│   ├── urls.py              
│   └── views.py             
├── 📁 qube_project           
│   ├── asgi.py              
│   ├── settings.py          
│   ├── urls.py              
│   └── wsgi.py              
├── run_project.bat          
├── run_project.py           
└── run_project.sh           
```

## Funkcjonalności

### Autoryzacja
- ✅ Własny system logowania bez Django Auth
- ✅ Rejestracja użytkowników
- ✅ Bezpieczne przechowywanie haseł (hashowanie)
- ✅ Obsługa sesji przez signed cookies
- ✅ Wylogowywanie

### Grupy
- ✅ Tworzenie grup projektowych
- ✅ Definiowanie lidera grupy z rozszerzonymi uprawnieniami
- ✅ Dodawanie i zarządzanie członkami grupy
- ✅ Przypisywanie i edycja ról członków
- ✅ Przeglądanie wszystkich grup użytkownika
- ✅ Usuwanie grup przez liderów

### Zadania
- ✅ Tworzenie i edycja zadań w obrębie grupy
- ✅ Określanie priorytetów zadań (niski, średni, wysoki)
- ✅ Ustawianie terminów realizacji
- ✅ Śledzenie statusu zadań (Oczekujące, W trakcie, Zakończone)
- ✅ Przydzielanie zadań członkom grupy
- ✅ Filtrowanie i sortowanie zadań
- ✅ Usuwanie zadań podczas usuwania członków lub grup

### Konto użytkownika
- ✅ Edycja podstawowych danych profilu
- ✅ Zmiana hasła
- ✅ Przegląd przydzielonych zadań ze wszystkich grup
- ✅ Identyfikacja grup, w których użytkownik jest liderem

## Technologie

Projekt QUBE wykorzystuje następujące technologie i narzędzia:

### Backend
- **Python 3.x** - język programowania
- **Django 4.x** - framework webowy
- **Neo4j** - baza danych grafowa
- **Neomodel** - OGM (Object Graph Mapper) dla Neo4j w Pythonie

### Frontend
- **HTML5/CSS3** - struktura i stylizacja
- **JavaScript** - interakcje po stronie klienta
- **CSS Grid/Flexbox** - responsywny układ strony

### Bezpieczeństwo
- **Django CSRF Protection** - ochrona przed atakami CSRF
- **Hashowanie haseł** - bezpieczne przechowywanie haseł
- **Zarządzanie sesją** - sesje oparte na podpisanych ciasteczkach

### Narzędzia deweloperskie
- **Git** - system kontroli wersji
- **Skrypty pomocnicze** - automatyczne uruchamianie projektu

## Architektura

### Model danych Neo4j

QUBE wykorzystuje bazę grafową Neo4j do reprezentowania złożonych relacji między encjami:

```
(UserNode) -[:BELONGS_TO]-> (Group)
(Group) -[:LEADS]-> (UserNode)
(Group) -[:HAS_MEMBER {role: string}]-> (UserNode)
(Group) -[:HAS_TASK]-> (Task)
(Task) -[:ASSIGNED_TO]-> (UserNode)
```

### Niestandardowy system autoryzacji

Projekt używa własnego systemu uwierzytelniania zamiast wbudowanego Django Auth, co demonstrowane jest w następujących plikach:
- `auth_utils.py` - funkcje pomocnicze do uwierzytelniania
- `forms.py` - formularze logowania i rejestracji
- `views.py` - obsługa logiki uwierzytelniania

To podejście pozwala na pełną integrację z bazą Neo4j bez potrzeby utrzymywania tradycyjnej bazy SQL wyłącznie dla autoryzacji.

### Interfejs użytkownika

UI QUBE został zaprojektowany z myślą o prostocie i użyteczności:
- Trójkolumnowy układ szczegółów grupy pokazujący zadania, powiązania i członków
- Dynamiczne modalne okna dla interakcji
- JavaScript do filtrowania i sortowania zadań bez przeładowywania strony
- Responsywny design dostosowujący się do różnych rozmiarów ekranu

## Przyszły rozwój

Planowane funkcjonalności i ulepszenia:

- ℹ️ Wyświetlanie szczegółów zadań w modalu zamiast przekierowania do osobnej strony
- ℹ️ Rozszerzony system powiadomień o zmianach w zadaniach i grupach
- ℹ️ Integracja kalendarza z terminami zadań
- ℹ️ Wizualizacja grafu zależności między zadaniami z wykorzystaniem Neo4j
- ℹ️ System komentarzy do zadań
- ℹ️ Zaawansowane statystyki i raporty dla liderów grup
- ℹ️ API REST/GraphQL do integracji z aplikacjami zewnętrznymi
- ℹ️ Przebudowa i rozszerzenie widoku ustawień użytkownika
- ℹ️ Wdrożenie systemu uprawnień na poziomie zadań

## Galeria
<div styles="display: block; margin: auto;">
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Strona główna</div>
    <img src="Docs/images/main.png" alt="main" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Widok logowania</div>
    <img src="Docs/images/logowanie.png" alt="logowanie" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Widok rejestracji</div>
    <img src="Docs/images/rejestracja.png" alt="rejestracja" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Widok strony głównej użytkownika</div>
    <img src="Docs/images/dashboard.png" alt="dashboard" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Widok tworzenia grupy</div>
    <img src="Docs/images/tworzenie_grupy.png" alt="tworzenie_grupy" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Widok ustawień</div>
    <img src="Docs/images/ustawienia.png" alt="ustawienia" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Widok grupy (jako członek)</div>
    <img src="Docs/images/szczeg_grupy.png" alt="szczeg_grupy" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Widok grupy (jako lider)</div>
    <img src="Docs/images/szeg_grupy_lider.png" alt="szczeg_grupy_lider" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Widok edycji członka</div>
    <img src="Docs/images/edycja_członka.png" alt="edycja_członka" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Widok edycji zadania</div>
    <img src="Docs/images/edycja_zadan.png" alt="edycja_zadan" width="600">
  </div>
  
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:12px; font-style:italic; margin-top:4px;">Komunikat przy usuwaniu członka z grupy</div>
    <img src="Docs/images/potw_usun.png" alt="potw_usun" width="600">
  </div>
<div>

## Autorzy

- Piotr Nowak ([GitHub](https://github.com/Puegoo))
- Łukasz Solecki ([GitHub](https://github.com/soleckilukasz))

## Licencja

Projekt jest udostępniany na licencji MIT.
