async function logout() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) {
        return;
    }
    logout2(accessToken);
}

async function logout2(accessToken) {
    try {
        let response = await fetch('/api/logout/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        })
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "アクセスに問題があります。ログインし直してください。");
        }
    } catch (error) {
        console.error('Error fetching:', error);
    }
    removeLocalAccessToken();
    removeLocalRefreshToken();
    // ログアウト後のリダイレクト
    window.location.hash = '#/'; // ログインページにリダイレクト
}