async function onSubmitLoginForm(event) {
    event.preventDefault();
    const identifier = document.getElementById('identifier').value;
    const password = document.getElementById('password').value;
    const otp = document.getElementById('otp') ? document.getElementById('otp').value : null;

    let loginData = { identifier, password };
    if (otp) {
        loginData.otp = otp;
    }

    try {
        let response = await fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });
        let data = await response.json();

        if (data.two_fa_required) {
            document.getElementById('2fa-field').style.display = 'flex';
            document.getElementById('message').textContent = '2FAコードを入力してください。';
        }
        if (response.ok) {
            setLocalAccessToken(data.access_token);
            setLocalRefreshToken(data.refresh_token);

            if (data.two_fa_required) {
                document.getElementById('2fa-field').style.display = 'flex';
                document.getElementById('message').textContent = '2FAコードを入力してください。';
            } else {
                window.location.hash = '#/home'; // homeページにリダイレクト
            }
        } else {
            //alert(JSON.stringify(data))
            if (data.detail) {
                document.getElementById('message').textContent = data.detail;
            } else if (data.error) {
                document.getElementById('message').textContent = data.error;
            } else {
                document.getElementById('message').textContent = 'ログインに失敗しました。';
            }
        }
    } catch(error) {
        console.error('Error:', error);
        document.getElementById('message').textContent = 'ログインに失敗しました。';
    }
}
