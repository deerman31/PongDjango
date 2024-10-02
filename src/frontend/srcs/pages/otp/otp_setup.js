async function refreshAccessToken() {
    try {
        const response = await fetch('/api/jwt/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'refresh_token': getLocalRefreshToken()
            })
        });
        const data = await response.json();
        if (response.ok) {
            setLocalAccessToken(data.access);
            return data.access;
        } else {
            alert('Error refreshing access token: ' + data.detail);
            return null;
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while refreshing the access token.');
        return null;
    }
}

async function generateQRCode() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    try {
        const response = await fetch('/api/generate-qr-code/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({})
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById('qr-code').src = 'data:image/png;base64,' + data.qr_code;
            document.getElementById('qr-code').style.display = 'block';
            document.getElementById('otp-verification').style.display = 'flex';
        } else {
            // アクセストークンが無効な場合、再度リフレッシュを試みる
            if (data.detail === 'Given token not valid for any token type' || data.detail === 'Token is invalid or expired') { 
                accessToken = await refreshAccessToken();
                if (accessToken) {
                    generateQRCode();  // 再度QRコード生成を試みる
                } else {
                    window.location.hash = '#/';
                }
            } else {
                throw new Error('Error generating QR code: ' + data.detail);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

async function verifyOTP(event) {
    event.preventDefault();
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }
    const otp = document.getElementById('otp').value;

    try {
        const response = await fetch('/api/verify-otp/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ otp })
        });
        const data = await response.json();
        document.getElementById('otp-verification').style.display = 'none';
        if (response.ok) {
            alert(data.detail);
            document.getElementById('qr-code').style.display = 'none';
        } else {
            throw new Error('Error : ' + data.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}

async function disable2FA() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    try {
        const response = await fetch('/api/disable-2fa/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({})
        });
        const data = await response.json();
        if (response.ok) {
            alert(data.detail)
            document.getElementById('qr-code').style.display = 'none';
        } else {
            throw new Error('Error : ' + data.detail);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
    }
}
