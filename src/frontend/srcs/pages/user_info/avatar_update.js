
async function getUserAvatar() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    try {
        //let response = await fetch('/api/auth/users/me/', {
        let response = await fetch('/api/get/avatar/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        })
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "アクセスに問題があります。ログインし直してください。");
        }
        const data = await response.json();

        const avatarImg = document.getElementById('current-avatar');
        if (data.avatar) {
            avatarImg.src = data.avatar;
        } else {
            //avatarImg.src = "../../../media/avatars/default/alaba.jpeg";
            avatarImg.src = "../../../media/avatars/default/default-avatar.png";
            avatarImg.alt = 'アバターは設定されていません';
        }
        console.log(avatarImg.src);
    } catch (error) {
        console.error('Error fetching current avatar:', error);
        alert(error.message);
    }
}

async function updateAvatar() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }
    const newAvatarFile = document.getElementById('new-avatar').files[0];
    
    const messageElement = document.getElementById('message');
    try {
        if (newAvatarFile) {
            const formData = new FormData();
            formData.append('avatar', newAvatarFile);
            let response = await fetch('/api/set/avatar/', {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                },
                body: formData
            })
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || "アクセスに問題があります。ログインし直してください。");
            }
            const data = await response.json();
            console.log("data: ", data);
            if (data) {
                messageElement.textContent = 'アバターが更新されました';
                document.getElementById('current-avatar').src = data.avatar;
                document.getElementById('new-avatar').value = '';
                document.getElementById('new-avatar-preview-spinner').style.display = 'none';
                const avatarPreview = document.getElementById('new-avatar-preview');
                avatarPreview.style.display = 'none';
                avatarPreview.src = '';
            }
        } else {
            messageElement.textContent = '新しいアバターを選択してください。';
        }
    } catch (error) {
        console.error('Error fetching current avatar:', error);
        alert(error.message);
    }
}

async function deleteAvatar() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }
    
    try {
        let response = await fetch('/api/delete/avatar/', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            },
        })
    
        const messageElement = document.getElementById('message');
        if (response.status === 400) {
            throw new Error('アバターの削除に失敗しました');
        } else if (response.status === 401) {
            throw new Error("refresh_tokenに問題があります。ログインし直してください。");
        } else if (response.status === 403) {
            window.location.href = '/';
        } else if (response.status === 404) {
            document.getElementById('current-avatar').src = "../../../media/avatars/default/default-avatar.png";
            document.getElementById('current-avatar').alt = 'アバターは設定されていません';
            //alert('アバターが設定されていません');
            messageElement.textContent = 'アバターが設定されていません';
        } else {
            document.getElementById('current-avatar').src = "../../../media/avatars/default/default-avatar.png";
            document.getElementById('current-avatar').alt = 'アバターは設定されていません';
            messageElement.textContent = 'アバターが削除されました';
        }
        console.log(document.getElementById('current-avatar').src);
    } catch (error) {
        messageElement.textContent = error.message;
        console.error('Error updating avatar:', error);
    }
}

function onChangeAvatarPreview(event) {
    const newAvatarFile = event.target.files[0];
    if (newAvatarFile == null) {
        return;
    }
    const avatarPreview = document.getElementById('new-avatar-preview');
    const avatarPreviewSpinner = document.getElementById('new-avatar-preview-spinner');
    avatarPreview.style.display = 'none';
    avatarPreviewSpinner.style.display = undefined;
    const reader = new FileReader();
    reader.onload = function() {
        avatarPreview.src = reader.result;
        avatarPreview.style.display = 'block';
        avatarPreviewSpinner.style.display = 'none';
    }
    reader.readAsDataURL(newAvatarFile);
}

function onLoadUpdateAvatarPage(event) {
    if (event.detail !== '#/user_information/avatar_update') {
        return;
    }

    getUserAvatar();
}
window.removeEventListener('ftPageChanged', onLoadUpdateAvatarPage);
window.addEventListener('ftPageChanged', onLoadUpdateAvatarPage);
