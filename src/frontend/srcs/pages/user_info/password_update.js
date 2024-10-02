function clearPasswordFields() {
    document.getElementById('current-password').value = '';
    document.getElementById('new-password').value = '';
    document.getElementById('re-new-password').value = '';
}

async function updatePassword(event) {
    event.preventDefault();
    const newPassword = document.getElementById('new-password').value;
    const reNewPassword = document.getElementById('re-new-password').value;
    const currentPassword = document.getElementById('current-password').value;
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }
    
    try {
        //let response = await fetch('/api/auth/users/set_password/', {
        let response = await fetch('/api/update/password/', {
            //method: 'POST',
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                //'Authorization': `JWT ${accessToken}`
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ new_password: newPassword, re_new_password: reNewPassword, current_password: currentPassword})
        })
        if (!response.ok) {
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
        document.getElementById('message').textContent = 'パスワードの変更に成功しました';
        clearPasswordFields()
    } catch (error) {
        console.error('Error updating password:', error);
        document.getElementById('message').textContent = error.message;
    }
}
