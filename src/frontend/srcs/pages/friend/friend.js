async function onChangeUserSearchInput(event) {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    const query = event.target.value; // 仮にユーザーの入力をqueryとして取得
    if (!query) {
        searchResults.innerHTML = '';
        return;
    }
    try {
        let response = await fetch(`/api/search/?q=${query}`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        if (!response.ok) {
            throw new Error("access_tokenに問題があります。ログインし直してください。");
        }
        const data = await response.json();
        const searchResults = document.getElementById('searchResults');
        searchResults.innerHTML = '';
        data.forEach(user => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.textContent = `${user.name} (${user.email})`;
            const button = document.createElement('button');
            button.className = 'btn btn-outline-primary';
            button.textContent = 'フレンド招待';
            button.onclick = () => sendFriendRequest(user.id);
            li.appendChild(button);
            searchResults.appendChild(li);
        });
    } catch (error) {
        //alert(error.message);
        alert(`-1: ${error.message}`);
        window.location.hash = '#/';
    }
}

async function sendFriendRequest(userId) {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    try {
        let response = await fetch(`/api/send_request/${userId}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        if (!response.ok) {
            throw new Error("access_tokenに問題があります。ログインし直してください。");
        }
        const data = await response.json();
        if (data.status === 'ok') {
            alert('フレンド招待を送信しました');
        } else if (data.status === 'already_sent_or_friend') {
            alert('すでに招待を送信済み、または既にフレンドです');
        }
    } catch (error) {
        alert(`0: ${error.message}`);
        window.location.hash = '#/';
    } 
}

async function loadFriendRequests() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }
    try {
        let response = await fetch('/api/friend_requests/', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        })
        if (!response.ok) {
            throw new Error("access_tokenに問題があります。ログインし直してください。");
        }

        const data = await response.json();

        const requestList = document.getElementById('requestList');
        requestList.innerHTML = '';
        data.forEach(user => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.textContent = `${user.name} (${user.email})`;
            const btnGroup = document.createElement('li');
            btnGroup.className = 'btn-group reverse';
            btnGroup.setAttribute('role', 'group');
            const acceptButton = document.createElement('button');
            acceptButton.className = 'btn btn-outline-success px-3';
            acceptButton.style.zIndex = 1;
            acceptButton.textContent = '承認';
            acceptButton.onclick = () => respondFriendRequest(user.id, 'accept');
            const rejectButton = document.createElement('button');
            rejectButton.className = 'btn btn-outline-danger px-3';
            rejectButton.textContent = '拒否';
            rejectButton.onclick = () => respondFriendRequest(user.id, 'reject');
            btnGroup.appendChild(acceptButton);
            btnGroup.appendChild(rejectButton);
            li.appendChild(btnGroup);
            requestList.appendChild(li);
        });
    } catch (error) {
        alert(`1: ${error.message}`);
        window.location.hash = '#/';
    }
}

async function respondFriendRequest(userId, action) {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }
    try {
        let response = await fetch(`/api/respond_request/${userId}/${action}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        })
        if (!response.ok) {
            throw new Error("access_tokenに問題があります。ログインし直してください。");
        }
        const data = await response.json();
        if (data) {
            loadFriendRequests();
        }
    } catch (error) {
        alert(`2: ${error.message}`);
        window.location.hash = '#/';
    }

}

async function loadFriends() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }
    try {
        let response = await fetch('/api/friends/', {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        })
        const data = await response.json();
        const friendList = document.getElementById('friendList');
        friendList.innerHTML = '';
        data.forEach(user => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.textContent = user.name;
            const isOnlineSpan = document.createElement('span');
            isOnlineSpan.className = 'badge badge-pill';
            isOnlineSpan.className += user.is_online ? ' text-bg-primary' : ' text-bg-secondary';
            isOnlineSpan.textContent = user.is_online ? 'オンライン' : 'オフライン';
            li.appendChild(isOnlineSpan);
            friendList.appendChild(li);
        });
    } catch (error) {
        alert(`3: ${error.message}`);
        window.location.hash = '#/';
    }
}

async function getFriendLists() {


    loadFriendRequests();


    loadFriends();
}

function onLoadFriendPage(event) {
    if (event.detail !== '#/friend') {
        return;
    }

    getFriendLists();
}
window.removeEventListener('ftPageChanged', onLoadFriendPage);
window.addEventListener('ftPageChanged', onLoadFriendPage);
