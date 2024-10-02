async function getUserEmail() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    try {
        //let response = await fetch('/api/auth/users/me/', {
        let response = await fetch('/api/get/email/', {
            method: 'GET',
            headers: {
                //'Authorization': `JWT ${accessToken}`
                'Authorization': `Bearer ${accessToken}`
            }
        })
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "アクセスに問題があります。ログインし直してください。");
        }
        const data = await response.json();
        if (data) {
            document.getElementById('current-email').value = data.email;
        }
    } catch (error) {
        console.error('Error fetching current email:', error);
    }
}

async function clearEmailFields() {
    document.getElementById('new-email').value = '';
}

async function updateEmail(event) {
    event.preventDefault();
    const newEmail = document.getElementById('new-email').value;
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    try {
        //let response = await fetch('/api/auth/users/set_email/', {
        let response = await fetch('/api/update/email/', {
            //method: 'POST',
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                //'Authorization': `JWT ${accessToken}`
                'Authorization': `Bearer ${accessToken}`
            },
            //body: JSON.stringify({ new_email: newEmail, re_new_email: reNewEmail, current_password: currentPassword })
            body: JSON.stringify({ email: newEmail })
        })
        if (!response.ok) {
            document.getElementById('new-email').value = '';
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
        alert(`メールアドレスが更新されました: ${newEmail}`);
        await clearEmailFields();
        document.getElementById('current-email').value = newEmail;
    } catch (error) {
        alert(error.message);
        console.error('Error updating email:', error);
    }
}

function onLoadUpdateEmailPage(event) {
    if (event.detail !== '#/user_information/email') {
        return;
    }

    getUserEmail();
}
window.removeEventListener('ftPageChanged', onLoadUpdateEmailPage);
window.addEventListener('ftPageChanged', onLoadUpdateEmailPage);
