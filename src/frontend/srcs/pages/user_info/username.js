async function getUserName() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    try {
        //let response = await fetch('/api/auth/users/me/', {
        let response = await fetch('/api/get/name/', {
            method: 'GET',
            headers: {
                //'Authorization': `JWT ${accessToken}`
                'Authorization': `Bearer ${accessToken}`
            }
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "アクセスに問題があります。ログインし直してください。");
        }
        const data = await response.json();
        if (data) {
            document.getElementById('current-username').value = data.name;
        }

    } catch (error) {
        alert(error.message);
        //window.location.href = '/';
    }
}

async function updateUsername(event) {
    event.preventDefault();
    const newUsername = document.getElementById('new-username').value;
    const messageElement = document.getElementById('message');
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    // ユーザー名のバリデーション
    if (!newUsername) {
        messageElement.textContent = 'ユーザー名を入力してください。';
        return; // 空文字の場合、処理を中断
    }

    const usernamePattern = /^[a-zA-Z0-9]{4,15}$/;
    if (!usernamePattern.test(newUsername)) {
        messageElement.textContent = 'ユーザー名は半角英数字のみで4文字以上15文字以内にしてください。';
        return; // バリデーションに失敗した場合、処理を中断
    }
    //updateUsernameRequest(accessToken, newUsername, messageElement);
    try {
        //let response = await fetch('/api/username_update/', {


        let response = await fetch('/api/update/name/', {
            //method: 'POST',
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                //'Authorization': `JWT ${accessToken}`
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ name: newUsername })
        });
        if (!response.ok) {
            document.getElementById('new-username').value = '';
            const errorData = await response.json();
            let errorMessage = '';
            if (typeof errorData === 'object' && errorData !== null) {
                for (const [key, value] of Object.entries(errorData)) {
                    errorMessage += `${value}\n`;
                }
            } else {
                errorMessage += errorData.error;
            }
            throw new Error(errorMessage || "アクセスに問題があります。ログインし直してください。");
        }
        const data = await response.json();
        if (data) {
            alert(`ユーザー名が更新されました: ${newUsername}`);
            document.getElementById('current-username').value = newUsername;
            document.getElementById('new-username').value = '';
            messageElement.textContent = '';
        }
    } catch (error) {
        alert(error.message);
        console.error('Error updating name:', error);
        //window.location.hash = '#/';
    }
}

function onLoadUpdateUserNamePage(event) {
    if (event.detail !== '#/user_information/username') {
        return;
    }

    getUserName();
}
window.removeEventListener('ftPageChanged', onLoadUpdateUserNamePage);
window.addEventListener('ftPageChanged', onLoadUpdateUserNamePage);
