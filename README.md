# QUBE

<img src="Docs/images/QUBE_banner.png" width="80vh" alt="Baner">

## Spis treści
1. [Wprowadzenie](#wprowadzenie)
2. [Instalacja](#instalacja)
3. [Struktura projektu](#struktura-projektu)
4. [Funkcjonalności](#funkcjonalności)
5. [Przyszły rozwój](#przyszły-rozwój)
6. [Galeria](#galeria)
7. [Autorzy](#autorzy)

## Wprowadzenie

...


## Instalacja

Aby uruchomić projekt, wykonaj następujące kroki:

1. Zainstaluj bazę danych Neo4j.
2. W pliku konfiguracyjnym Neo4j ustaw wartość `dbms.security.auth_enabled` na `false`.
3. Uruchom plik `run_project.bat` (dla systemu Windows) lub `run_project.sh` (dla systemów macOS i Linux).

Po wykonaniu tych czynności projekt samoczynnie skonfiguruje bazę i załaduje do niej niezbędne dane.

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
│   │   ├── errors
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

**Autoryzacja:**
- ✅ Logowanie
- ✅ Rejestracja
- ✅ Wylogowywanie

**Grupy:**
- ✅ Tworzenie grup
- ✅ Tworzenie lidera grupy
- ✅ Dodawanie i modyfikacja członków grupy
- ✅ Przeglądanie grup
- ✅ Przeglądanie członków grupy
- ✅ Usuwanie grupy

**Zadania:**
- ✅ Dodawanie i modyfikacja zadań w grupie
- ✅ Przeglądanie zadań

**Konto:**
- ✅ Edycja danych konta

## Przyszły rozwój

- ℹ️ Zależność zadań
- ℹ️ Przydzielanie zadań kilku członkom grupy
- ℹ️ Usuwanie zakończonych zadań
- ℹ️ Wyświetlanie szczegółów zadań w modalu
- ℹ️ Poprawa wizualna kilku elementów

## Galeria

<figure>
  <img src="Docs/images/dashboard.png" alt="dashboard" width="600">
  <figcaption>dashboard.png</figcaption>
</figure>

<figure>
  <img src="Docs/images/edycja_członka.png" alt="edycja_członka" width="600">
  <figcaption>edycja_członka.png</figcaption>
</figure>

<figure>
  <img src="Docs/images/edycja_zadan.png" alt="edycja_zadan" width="600">
  <figcaption>edycja_zadan.png</figcaption>
</figure>

<figure>
  <img src="Docs/images/logowanie.png" alt="logowanie" width="600">
  <figcaption>logowanie.png</figcaption>
</figure>

<figure>
  <img src="Docs/images/main.png" alt="main" width="600">
  <figcaption>main.png</figcaption>
</figure>

<figure>
  <img src="Docs/images/potw_usun.png" alt="potw_usun" width="600">
  <figcaption>potw_usun.png</figcaption>
</figure>

<figure>
  <img src="Docs/images/rejestracja.png" alt="rejestracja" width="600">
  <figcaption>rejestracja.png</figcaption>
</figure>

<figure>
  <img src="Docs/images/szczeg_grupy.png" alt="szczeg_grupy" width="600">
  <figcaption>szczeg_grupy.png</figcaption>
</figure>

<figure>
  <img src="Docs/images/tworzenie_grupy.png" alt="tworzenie_grupy" width="600">
  <figcaption>tworzenie_grupy.png</figcaption>
</figure>

<figure>
  <img src="Docs/images/ustawienia.png" alt="ustawienia" width="600">
  <figcaption>ustawienia.png</figcaption>
</figure>


## Autorzy

- Piotr Nowak ([GitHub](https://github.com/Puegoo))
- Łukasz Solecki ([GitHub](https://github.com/soleckilukasz))
