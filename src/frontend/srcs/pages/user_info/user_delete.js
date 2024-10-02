async function deleteUserRequest(event) {
    event.preventDefault();
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }
    const current_password = document.getElementById('current_password').value;

    try {
        //let response = await fetch('/api/auth/users/me/', {
        let response = await fetch('/api/delete/user/', {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ current_password })
        })
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Userの削除に失敗しました。");
        }
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        document.getElementById('responseMessage').textContent = "アカウントの削除に成功しました。";
        alert("アカウントの削除に成功しました。");
        window.location.hash = '#/';
    } catch (error) {
        alert(error.message);
    }
}
