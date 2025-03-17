/**
 * Dodaje użytkownika o podanym username do listy członków,
 * usuwając go jednocześnie z listy "wszystkich użytkowników".
 */
function addMember(username) {
  const userItem = document.getElementById(`user_${username}`);
  if (!userItem) return;

  userItem.remove(); // usunięcie z listy po prawej

  const li = document.createElement('li');
  li.className = 'member-item';
  li.dataset.username = username;
  li.innerHTML = `
    <span>${username}</span>
    <span class="member-role">
      &nbsp;
      <input
        type="text"
        name="role_${username}"
        class="role-input"
        placeholder="Dowolna rola..."
      >
    </span>
    <button
      type="button"
      class="square-btn remove-btn"
      onclick="removeMember('${username}')"
    >
      -
    </button>
    <input type="hidden" name="members" value="${username}">
  `;

  const memberList = document.getElementById('memberList');
  if (memberList) {
    memberList.appendChild(li);
  }
}

/**
 * Usuwa użytkownika z listy członków i przywraca do "wszystkich użytkowników".
 */
function removeMember(username) {
  const memberItem = document.querySelector(`.member-item[data-username='${username}']`);
  if (!memberItem) return;

  memberItem.remove(); // usuń z listy członków

  const li = document.createElement('li');
  li.className = 'user-item';
  li.id = `user_${username}`;
  li.innerHTML = `
    <span>${username}</span>
    <button
      type="button"
      class="square-btn add-btn"
      onclick="addMember('${username}')"
    >
      +
    </button>
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

/* Ewentualne funkcje editTask(uid) / editTaskStatus(uid) / editMember(username) */
function editTask(uid) {
  alert(`Tu logika edycji zadania o uid=${uid}`);
}
function editTaskStatus(uid) {
  alert(`Tu logika zmiany statusu zadania o uid=${uid}`);
}
function editMember(username) {
  alert(`Tu logika edycji członka: ${username}`);
}