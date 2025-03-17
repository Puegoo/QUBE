/**
 * Dodaje użytkownika o podanym username do listy członków,
 * usuwając go jednocześnie z listy "wszystkich użytkowników".
 */
function addMember(username) {
  const userItem = document.getElementById(`user_${username}`);
  if (!userItem) return;

  // Usuwamy element z listy "wszystkich użytkowników"
  userItem.remove();

  // Tworzymy nowy element <li> dla listy członków
  const li = document.createElement('li');
  li.className = 'member-item';
  li.dataset.username = username;
  li.innerHTML = `
    <span>${username}</span>
    <span class="member-role">
      &nbsp;
      <input type="text" name="role_${username}" class="role-input" placeholder="Dowolna rola...">
    </span>
    <button type="button" class="square-btn remove-btn" onclick="removeMember('${username}')">-</button>
    <input type="hidden" name="members" value="${username}">
  `;
  
  const memberList = document.getElementById('memberList');
  if (memberList) {
    memberList.appendChild(li);
  }
}

/**
 * Usuwa użytkownika z listy członków i przywraca go do "wszystkich użytkowników".
 */
function removeMember(username) {
  const memberItem = document.querySelector(`.member-item[data-username='${username}']`);
  if (!memberItem) return;

  // Usuwamy element z listy członków
  memberItem.remove();

  // Tworzymy element <li> dla listy "wszystkich użytkowników"
  const li = document.createElement('li');
  li.className = 'user-item';
  li.id = `user_${username}`;
  li.innerHTML = `
    <span>${username}</span>
    <button type="button" class="square-btn add-btn" onclick="addMember('${username}')">+</button>
  `;

  const allUsersList = document.getElementById('allUsersList');
  if (allUsersList) {
    allUsersList.appendChild(li);
  }
}

/* Obsługa modali (dodawanie członka, dodawanie zadania) */
function openAddMemberModal() {
  const modal = document.getElementById('addMemberModal');
  if (modal) {
    modal.style.display = 'flex';
  }
}

function closeAddMemberModal() {
  const modal = document.getElementById('addMemberModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

function openAddTaskModal() {
  const modal = document.getElementById('addTaskModal');
  if (modal) {
    modal.style.display = 'flex';
  }
}

function closeAddTaskModal() {
  const modal = document.getElementById('addTaskModal');
  if (modal) {
    modal.style.display = 'none';
  }
}

/* Ewentualne funkcje edycji */
function editTask(uid) {
  alert(`Tu logika edycji zadania o uid=${uid}`);
}

function editTaskStatus(uid) {
  alert(`Tu logika zmiany statusu zadania o uid=${uid}`);
}

function editMember(username) {
  alert(`Tu logika edycji członka: ${username}`);
}

/* --- Mechanizm filtrowania zadań --- */
let currentFilter = ''; // Może być 'due_date', 'status' lub 'priority'
let sortAscending = true;

function setTaskFilter(filterName) {
  // Pobierz wszystkie przyciski filtrowania
  const filterButtons = document.querySelectorAll('.filter-btn');

  // Jeśli kliknięty filtr jest już aktywny, resetujemy filtr
  if (currentFilter === filterName) {
    filterButtons.forEach(btn => btn.classList.remove('active'));
    currentFilter = '';
    clearTaskFilter();
  } else {
    // Ustaw aktywny filtr – oznacz wybrany przycisk jako active
    filterButtons.forEach(btn => {
      if (btn.getAttribute('data-filter') === filterName) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
    currentFilter = filterName;
    applyTaskFilter(filterName);
  }
}

function toggleTaskSortOrder() {
  sortAscending = !sortAscending;
  const sortIcon = document.getElementById("taskSortIcon");
  if (sortAscending) {
    sortIcon.src = "/static/icons/ascending.svg";
    sortIcon.alt = "Sortuj rosnąco";
  } else {
    sortIcon.src = "/static/icons/descending.svg";
    sortIcon.alt = "Sortuj malejąco";
  }
  filterTasks();
}

function applyTaskFilter(filter) {
  filterTasks();
}

function clearTaskFilter() {
  // Przywróć widoczność wszystkich zadań
  const taskListItems = document.querySelectorAll('.task-list li');
  taskListItems.forEach(item => {
    item.style.display = 'block';
  });
}

function filterTasks() {
  // Pobierz wszystkie elementy <li> z listy zadań
  const taskListItems = document.querySelectorAll('.task-list li');
  let tasksArray = Array.from(taskListItems);

  // Jeśli nie ma aktywnego filtra, pokazujemy wszystkie zadania
  if (!currentFilter) {
    tasksArray.forEach(item => item.style.display = 'block');
    return;
  }

  // Filtrowanie elementów na podstawie atrybutu data-<filter>
  tasksArray.forEach(item => {
    const value = item.getAttribute('data-' + currentFilter);
    if (!value) {
      item.style.display = 'none';
    } else {
      item.style.display = 'block';
    }
  });

  // Sortowanie elementów
  if (currentFilter === 'due_date') {
    tasksArray.sort((a, b) => {
      let aDate = a.getAttribute('data-due_date') || '9999-12-31';
      let bDate = b.getAttribute('data-due_date') || '9999-12-31';
      return sortAscending ? aDate.localeCompare(bDate) : bDate.localeCompare(aDate);
    });
  } else if (currentFilter === 'status') {
    tasksArray.sort((a, b) => {
      let aStatus = a.getAttribute('data-status') || '';
      let bStatus = b.getAttribute('data-status') || '';
      return sortAscending ? aStatus.localeCompare(bStatus) : bStatus.localeCompare(aStatus);
    });
  } else if (currentFilter === 'priority') {
    tasksArray.sort((a, b) => {
      let aPriority = a.getAttribute('data-priority') || '';
      let bPriority = b.getAttribute('data-priority') || '';
      const order = { 'high': 3, 'medium': 2, 'low': 1 };
      return sortAscending ? order[aPriority] - order[bPriority] : order[bPriority] - order[aPriority];
    });
  }

  // Aktualizacja listy z posortowanymi elementami
  const taskList = document.querySelector('.task-list');
  taskList.innerHTML = '';
  tasksArray.forEach(item => taskList.appendChild(item));
}