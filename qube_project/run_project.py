#!/usr/bin/env python3
import socket
import subprocess
import sys
import time
import webbrowser

def check_neo4j(host='localhost', port=7687, timeout=5):
    """Sprawdza, czy serwer Neo4j jest dostępny na podanym porcie."""
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return True
    except OSError:
        return False

def run_command(command, shell=False):
    """Uruchamia podaną komendę i kończy skrypt, jeśli wystąpi błąd."""
    print(f"Uruchamiam: {' '.join(command) if isinstance(command, list) else command}")
    result = subprocess.run(command, shell=shell)
    if result.returncode != 0:
        print(f"Błąd przy komendzie: {command}")
        sys.exit(result.returncode)

def main():
    # Sprawdzenie, czy Neo4j działa
    if not check_neo4j():
        print("Błąd: Neo4j nie jest uruchomiony. Uruchom Neo4j i spróbuj ponownie.")
        sys.exit(1)
    
    # Instalacja wymaganych pakietów
    run_command([sys.executable, "-m", "pip", "install", "neomodel"])
    run_command([sys.executable, "-m", "pip", "install", "django"])
    
    # Uruchomienie migracji
    run_command([sys.executable, "manage.py", "makemigrations"])
    run_command([sys.executable, "manage.py", "migrate"])
    
    # Seed danych – upewnij się, że masz komendę seed_data w appce (np. jako custom management command)
    run_command([sys.executable, "manage.py", "seed_data"])
    
    # Uruchomienie serwera Django w tle
    print("Uruchamiam serwer Django...")
    server_process = subprocess.Popen([sys.executable, "manage.py", "runserver"])
    
    # Poczekaj kilka sekund, aby serwer wystartował
    time.sleep(3)
    
    # Otwórz domyślną przeglądarkę
    webbrowser.open("http://127.0.0.1:8000/")
    
    # Czekaj aż serwer zostanie zatrzymany
    server_process.wait()

if __name__ == '__main__':
    main()
