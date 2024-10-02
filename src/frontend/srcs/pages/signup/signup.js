function onSubmitSignUpForm(event) {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const re_password = document.getElementById('re_password').value;
    
    //fetch('/auth/users/', {
    fetch('/api/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, email, password, re_password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message == "ユーザーが正常に作成されました") {
            window.location.hash = '#/login'; // ログインページにリダイレクト
            // document.getElementById('message').textContent = 'サインアップ成功！';
        } else {
            if (data.error) {
                document.getElementById('message').textContent = data.error;
            } else {
                document.getElementById('message').textContent = 'サインアップに失敗しました。';
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('message').textContent = 'サインアップに失敗しました。';
    });
}
