/**
 * Dodaje użytkownika o podanym username do listy członków,
 * usuwając go jednocześnie z listy użytkowników (po prawej).
 */
function addMember(username) {
    // Szukamy elementu w liście po prawej (id="user_username")
    const userItem = document.getElementById(`user_${username}`);
    if (!userItem) return;
  
    // Usuwamy z listy "wszystkich użytkowników"
    userItem.remove();
  
    // Tworzymy nowy <li> w liście członków (id="memberList")
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
  
    // Dodajemy nowy element do listy członków
    const memberList = document.getElementById('memberList');
    if (memberList) {
      memberList.appendChild(li);
    }
  }
  
  /**
   * Usuwa użytkownika o podanym username z listy członków
   * i przywraca go do listy "wszystkich użytkowników".
   */
  function removeMember(username) {
    // Szukamy <li> w liście członków po atrybucie data-username
    const memberItem = document.querySelector(`.member-item[data-username='${username}']`);
    if (!memberItem) return;
  
    // Usuwamy z listy członków
    memberItem.remove();
  
    // Odzyskujemy element <li> w liście "wszystkich użytkowników"
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
  
    // Dodajemy do listy użytkowników (id="allUsersList")
    const allUsersList = document.getElementById('allUsersList');
    if (allUsersList) {
      allUsersList.appendChild(li);
    }
  }
  
  function openAddMemberModal() {
    const modal = document.getElementById('addMemberModal');
    if (modal) {
        modal.style.display = 'flex'  // pokaż modal
    }
  }
  
  function closeAddMemberModal() {
    const modal = document.getElementById('addMemberModal');
    if (modal) {
      modal.style.display = 'none';   // schowaj modal
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
  