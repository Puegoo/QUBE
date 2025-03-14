function addMember(username) {
    const userItem = document.getElementById('user_' + username);
    if (!userItem) return;
  
    // Usuwamy z listy po prawej
    userItem.remove();
  
    // Tworzymy element <li> dla listy członków
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
    document.getElementById('memberList').appendChild(li);
  }
  
  function removeMember(username) {
    const memberItem = document.querySelector(`.member-item[data-username='${username}']`);
    if (!memberItem) return;
  
    // Usuwamy z listy członków
    memberItem.remove();
  
    // Przywracamy do listy po prawej
    const li = document.createElement('li');
    li.className = 'user-item';
    li.id = 'user_' + username;
    li.innerHTML = `
      <span>${username}</span>
      <button type="button" class="square-btn add-btn" onclick="addMember('${username}')">+</button>
    `;
    document.getElementById('allUsersList').appendChild(li);
  }
  