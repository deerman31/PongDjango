function getLocalAccessToken() {
    return localStorage.getItem('access_token');
}
function getLocalRefreshToken() {
    return localStorage.getItem('refresh_token');
}
function setLocalAccessToken(token) {
    localStorage.setItem('access_token', token);
}
function setLocalRefreshToken(token) {
    localStorage.setItem('refresh_token', token);
}
function removeLocalAccessToken() {
    localStorage.removeItem('access_token');
}
function removeLocalRefreshToken() {
    localStorage.removeItem('refresh_token');
}

async function verifyAndFetchToken() {
    const result = await verifyToken();
    if (result.ok) {
        return getLocalAccessToken();
    } else {
        console.log("FAIL:", result.data);
        let token = getLocalAccessToken();
        logout2(token);
        return null;
    }
}

async function verifyToken() {
    var access_token = getLocalAccessToken();
    if (!access_token) { // tokenがない場合は、indexにリダイレクトとさせる
        return { ok: false, error: "access_tokenに問題があります。ログインし直してください。" };
    }
    try {
        let response = await fetch('/api/jwt/verify/', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({access_token})
        });
        if (response.status === 400) {
            return { ok: false, error: "access_tokenに問題があります。ログインし直してください。" };
        } else if (response.status === 401) {
            const refresh_token = getLocalRefreshToken();
            if (!refresh_token) { // tokenがない場合は、indexにリダイレクトとさせる
                return { ok: false, error: "refresh_tokenに問題があります。ログインし直してください。" };
            }
            response = await fetch('/api/jwt/refresh/', {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({refresh_token})
            });
            if (!response.ok) {
                return { ok: false, error: "refresh_tokenに問題があります。ログインし直してください。" };
            } else {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                return { ok: true, data };
            }
        }
        if (response.ok) {
            const data = await response.json();
            return { ok: true, data };
        } else {
            return { ok: false, error: "予期せぬエラーが発生しました。" };
        }
    } catch (error) {
        return { ok: false, error: "エラーが発生しました: " + error.toString() };
    }
}