if (!window.groupDetailScriptLoaded) {
  window.groupDetailScriptLoaded = true;

  // Upewnij się, że zmienna currentGroupUid została zadeklarowana w szablonie przed dołączeniem tego pliku!
  if (typeof currentGroupUid === 'undefined') {
    console.error("currentGroupUid is not defined. Upewnij się, że zmienna jest zadeklarowana w szablonie przed dołączeniem script.js.");
  }

  // Globalne zmienne filtrowania
  window.currentFilter = ''; // może być 'due_date', 'status', 'priority' lub 'blocked'
  window.sortAscending = true;

  /**
   * Dodaje użytkownika o podanym username do listy członków,
   * usuwając go jednocześnie z listy "wszystkich użytkowników".
   */
  window.addMember = function(username) {
    const userItem = document.getElementById(`user_${username}`);
    if (!userItem) return;

    userItem.remove();

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
  };

  /**
   * Usuwa użytkownika z listy członków i przywraca go do "wszystkich użytkowników".
   */
  window.removeMember = function(username) {
    const memberItem = document.querySelector(`.member-item[data-username='${username}']`);
    if (!memberItem) return;

    memberItem.remove();

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
  };

  /* Obsługa modali dla dodawania członków i zadań */
  window.openAddMemberModal = function() {
    const modal = document.getElementById('addMemberModal');
    if (modal) modal.style.display = 'flex';
  };
  window.closeAddMemberModal = function() {
    const modal = document.getElementById('addMemberModal');
    if (modal) modal.style.display = 'none';
  };
  window.openAddTaskModal = function() {
    const modal = document.getElementById('addTaskModal');
    if (modal) modal.style.display = 'flex';
  };
  window.closeAddTaskModal = function() {
    const modal = document.getElementById('addTaskModal');
    if (modal) modal.style.display = 'none';
  };

  /* Funkcje edycji – przekierowanie do widoków edycji */
  window.editTask = function(uid) {
    window.location.href = `/group/${currentGroupUid}/edit_task/${uid}/`;
  };
  window.editTaskStatus = function(uid) {
    window.location.href = `/group/${currentGroupUid}/edit_task/${uid}/`;
  };
  window.editMember = function(username) {
    window.location.href = `/group/${currentGroupUid}/edit_member/${username}/`;
  };

  /* Mechanizm filtrowania zadań */
  window.setTaskFilter = function(filterName) {
    const filterButtons = document.querySelectorAll('.filter-btn');
    if (window.currentFilter === filterName) {
      filterButtons.forEach(btn => btn.classList.remove('active'));
      window.currentFilter = '';
      clearTaskFilter();
    } else {
      filterButtons.forEach(btn => {
        if (btn.getAttribute('data-filter') === filterName) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
      window.currentFilter = filterName;
      applyTaskFilter(filterName);
    }
  };

  window.toggleTaskSortOrder = function() {
    window.sortAscending = !window.sortAscending;
    const sortIcon = document.getElementById("taskSortIcon");
    if (sortIcon) {
      if (window.sortAscending) {
        sortIcon.src = "/static/icons/ascending.svg";
        sortIcon.alt = "Sortuj rosnąco";
      } else {
        sortIcon.src = "/static/icons/descending.svg";
        sortIcon.alt = "Sortuj malejąco";
      }
    }
    filterTasks();
  };

  window.applyTaskFilter = function(filter) {
    filterTasks();
  };

  window.clearTaskFilter = function() {
    const taskListItems = document.querySelectorAll('.task-list li');
    taskListItems.forEach(item => item.style.display = 'block');
  };

  window.filterTasks = function() {
    const taskListItems = document.querySelectorAll('.task-list li');
    let tasksArray = Array.from(taskListItems);
    if (!window.currentFilter) {
      tasksArray.forEach(item => item.style.display = 'block');
      return;
    }

    // Ukrywamy zadania, które nie spełniają kryteriów
    tasksArray.forEach(item => {
      let value;
      if (window.currentFilter === 'blocked') {
        value = item.getAttribute('data-blocked');
        // Pokazujemy tylko zablokowane zadania gdy filtr jest aktywny
        item.style.display = (value === 'True' || value === 'true') ? 'block' : 'none';
      } else {
        value = item.getAttribute('data-' + window.currentFilter);
        item.style.display = value ? 'block' : 'none';
      }
    });

    // Sortowanie według aktywnego filtra
    if (window.currentFilter === 'due_date') {
      tasksArray.sort((a, b) => {
        let aDate = a.getAttribute('data-due_date') || '9999-12-31';
        let bDate = b.getAttribute('data-due_date') || '9999-12-31';
        return window.sortAscending ? aDate.localeCompare(bDate) : bDate.localeCompare(aDate);
      });
    } else if (window.currentFilter === 'status') {
      tasksArray.sort((a, b) => {
        let aStatus = a.getAttribute('data-status') || '';
        let bStatus = b.getAttribute('data-status') || '';
        return window.sortAscending ? aStatus.localeCompare(bStatus) : bStatus.localeCompare(aStatus);
      });
    } else if (window.currentFilter === 'priority') {
      tasksArray.sort((a, b) => {
        let aPriority = a.getAttribute('data-priority') || '';
        let bPriority = b.getAttribute('data-priority') || '';
        const order = { 'high': 3, 'medium': 2, 'low': 1 };
        return window.sortAscending ? order[aPriority] - order[bPriority] : order[bPriority] - order[aPriority];
      });
    } else if (window.currentFilter === 'blocked') {
      tasksArray.sort((a, b) => {
        let aBlocked = a.getAttribute('data-blocked') === 'true';
        let bBlocked = b.getAttribute('data-blocked') === 'true';
        return window.sortAscending ? aBlocked - bBlocked : bBlocked - aBlocked;
      });
    }

    // Odświeżamy listę zadań z zachowaniem sortowania
    const taskList = document.querySelector('.task-list');
    if (taskList) {
      taskList.innerHTML = '';
      tasksArray.forEach(item => taskList.appendChild(item));
    }
  };

  /* Mechanizm edycji nazwy grupy przez modal (tylko dla lidera) */
  window.openEditGroupNameModal = function() {
    const modal = document.getElementById("editGroupNameModal");
    if (modal) modal.style.display = "flex";
  };
  window.closeEditGroupNameModal = function() {
    const modal = document.getElementById("editGroupNameModal");
    if (modal) modal.style.display = "none";
  };
  window.saveGroupNameModal = function() {
    const newName = document.getElementById("modalGroupNameInput").value.trim();
    console.log("Nowa nazwa:", newName);
    if (!newName) {
      alert("Podaj nową nazwę grupy.");
      return;
    }
    updateGroupName(newName);
  };

  window.updateGroupName = function(newName) {
    console.log("Wysyłanie nowej nazwy:", newName);
    fetch(`/group/${currentGroupUid}/update-name/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify({ "name": newName })
    })
    .then(response => response.json())
    .then(data => {
      console.log("Odpowiedź z serwera:", data);
      if (data.success) {
        const groupNameDisplay = document.getElementById("groupNameDisplay");
        if (groupNameDisplay) {
          groupNameDisplay.innerText = newName;
        }
        closeEditGroupNameModal();
      } else {
        alert("Błąd aktualizacji nazwy grupy: " + data.error);
      }
    })
    .catch(error => {
      console.error("Błąd:", error);
      alert("Wystąpił błąd podczas aktualizacji.");
    });
  };

  // Funkcje obsługujące modal potwierdzający usunięcie członka
  window.openDeleteConfirmModal = function() {
    const modal = document.getElementById('deleteConfirmModal');
    if (modal) modal.style.display = 'flex';
  };

  window.closeDeleteConfirmModal = function() {
    const modal = document.getElementById('deleteConfirmModal');
    if (modal) modal.style.display = 'none';
  };

  window.confirmDeleteMember = function() {
    const confirmUsernameInput = document.getElementById('confirmUsername');
    const enteredUsername = confirmUsernameInput ? confirmUsernameInput.value.trim() : "";
    const memberUsername = document.getElementById('memberUsername').textContent.trim();
    
    // Jeśli nie wpisano poprawnej nazwy, pokazujemy alert
    if (enteredUsername !== memberUsername) {
      alert("Wpisana nazwa nie zgadza się z nazwą członka!");
      return;
    }
    
    const deleteInput = document.getElementById('deleteInput');
    const deleteTasksCheckbox = document.getElementById('deleteTasksCheckbox');
    const deleteTasksInput = document.getElementById('deleteTasksInput');

    if (deleteInput) {
      deleteInput.value = "1";
    }
    if (deleteTasksInput) {
      deleteTasksInput.value = deleteTasksCheckbox.checked ? "1" : "0";
    }
    
    const form = document.getElementById('editMemberForm');
    if (form) {
      form.submit();
    }
  };

  /* Funkcje zarządzania ukończonymi zadaniami */
  window.openCompletedTasksModal = function() {
    const modal = document.getElementById('completedTasksModal');
    if (modal) modal.style.display = 'flex';
  };

  window.closeCompletedTasksModal = function() {
    const modal = document.getElementById('completedTasksModal');
    if (modal) modal.style.display = 'none';
  };

  window.toggleAllCompletedTasks = function() {
    const selectAllCheckbox = document.getElementById('selectAllCompleted');
    const taskCheckboxes = document.querySelectorAll('.task-checkbox');
    
    taskCheckboxes.forEach(checkbox => {
      checkbox.checked = selectAllCheckbox.checked;
    });
  };

  window.confirmDeleteAllCompleted = function() {
    if (confirm('Czy na pewno chcesz usunąć wszystkie ukończone zadania? Ta operacja jest nieodwracalna.')) {
      const deleteAllInput = document.getElementById('deleteAllInput');
      if (deleteAllInput) {
        deleteAllInput.value = "1";
        document.getElementById('completedTasksForm').submit();
      }
    }
  };

  // Funkcja pomocnicza do pobierania CSRF tokenu z ciasteczek
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
}

function confirmDeleteTask(taskUid, taskTitle) {
  const modal = document.getElementById('deleteTaskConfirmModal');
  const taskTitleElement = document.getElementById('taskTitleToDelete');
  
  if (modal && taskTitleElement) {
    taskTitleElement.textContent = taskTitle;
    modal.style.display = 'flex';
  }
  
  return false;
}

function closeDeleteTaskModal() {
  const modal = document.getElementById('deleteTaskConfirmModal');
  if (modal) {
    modal.style.display = 'none';
  }
}