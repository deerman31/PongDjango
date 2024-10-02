async function room_in() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    const wsUrl = `ws/single_game/?token=${accessToken}`;
    // console.log(wsUrl);
    window.roomSocket = new WebSocket(wsUrl);

    window.roomSocket.onopen = function(event) {
        console.log('WebSocket connection opened:', event);
    };

    window.roomSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === 'start_game') {
            startSinglePongGame();
        } else if (data.type === 'drawing') {
            let m = JSON.parse(data.message);
            updateSinglePongGame(m);
        } else if (data.type === 'game_end') {
            const canvas = document.getElementById('pong-game');
            const ctx = canvas.getContext('2d');
            canvas.style.display = 'none';
            document.getElementById('status-message').style.display = 'block';
            document.getElementById('move-btn-group').style.display = 'none';
            safeCloseSingleGameWebSocket(1000, 'finish')
            window.location.hash = '#/home';
        }
    };

    window.roomSocket.onclose = function(event) {
        console.log('WebSocket closed:', event);
        // ここで`window.roomSocket`の操作が不要であれば削除するか、`null`チェックを追加します
        if (window.roomSocket) {
            window.roomSocket = null;
        }
    };

    window.roomSocket.onerror = function(event) {
        console.error('WebSocket error:', event);
    };


}

function startSinglePongGame() {
    document.getElementById('status-message').style.display = 'none';
    document.getElementById('move-btn-group').style.display = 'block';
    const canvas = document.getElementById('pong-game');
    const ctx = canvas.getContext('2d');
    canvas.style.display = 'block';

    // 初期描画
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // ラケットの初期位置やボールの初期位置などを描画
    ctx.fillStyle = '#fff';

    ctx.fillRect(0, 250, 10, 100); // player 1
    ctx.fillRect(760, 250, 10, 100); // player 2

    ctx.beginPath();
    ctx.arc(400, 300, 10, 0, Math.PI * 2); // ball
    ctx.fill();
}

function updateSinglePongGame(data) {
    const canvas = document.getElementById('pong-game');
    const ctx = canvas.getContext('2d');

    // if (data.game_over) {
    //     alert("ゲームオーバー");
    //     // ゲームオーバー時の処理をここに追加
    //     return;
    // }

    // 画面をクリア
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 背景
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // プレイヤー1のラケット
    ctx.fillStyle = '#fff';
    // ctx.fillRect(10, data.player_1_y, 10, 100);
    ctx.fillRect(0, data.player_1_y, 10, 100);

    // プレイヤー2のラケット
    ctx.fillStyle = '#fff';
    ctx.fillRect(760, data.player_2_y, 10, 100);
    // ctx.fillRect(790, data.player_2_y, 10, 100);

    // ボール
    ctx.beginPath();
    ctx.arc(data.ball_x, data.ball_y, 10, 0, Math.PI * 2);
    ctx.fill();

    // スコア表示
    ctx.font = "30px Arial";
    ctx.fillText(data.score_1, 360, 50);
    ctx.fillText(data.score_2, 420, 50);
}

function onSingleGameAction(action) {
    window.roomSocket.send(JSON.stringify({'action': action}));
}

function singleGameHandleKeydown(event) {
    let action = null;
    //if (event.key === 'ArrowUp') {
    if (event.key === 'k') {
        onSingleGameAction('up');
    //} else if (event.key === 'ArrowDown') {
    } else if (event.key === 'j') {
        onSingleGameAction('down');
    }
    //console.log(action)
    //console.log(event)
}

function safeCloseSingleGameWebSocket(code, reason) {
    window.removeEventListener('keydown', singleGameHandleKeydown);
    window.removeEventListener('hashchange', singleGameHandleHashchange);
    window.removeEventListener('beforeunload', singleGameHandleBeforeunload);
    window.removeEventListener('popstate', singleGameHandlePopstate);
    if (window.roomSocket && window.roomSocket.readyState === WebSocket.OPEN) {
    //if (window.roomSocket) {
        window.roomSocket.close(code, reason);
        window.roomSocket = null; // WebSocket を解放する
    }
}

function singleGameHandleHashchange(event) {
    console.log("hashchange")
    safeCloseSingleGameWebSocket(4003, "hashchange");
}
function singleGameHandleBeforeunload(event) {
    console.log("beforeunload")
    safeCloseSingleGameWebSocket(4002, "beforeunload");
}
function singleGameHandlePopstate(event) {
    console.log("popstate")
    safeCloseSingleGameWebSocket(4001, "popstate");
}

async function onLoadSingleGamePage(event) {
    if (event.detail !== '#/single_game') {
        return;
    }

    // codeは適当
    safeCloseSingleGameWebSocket(4000, 'load');

    room_in();
    window.addEventListener('keydown', singleGameHandleKeydown);
    window.addEventListener('hashchange', singleGameHandleHashchange);
    window.addEventListener('beforeunload', singleGameHandleBeforeunload);
    window.addEventListener('popstate', singleGameHandlePopstate);
}
window.removeEventListener('ftPageChanged', onLoadSingleGamePage);
window.addEventListener('ftPageChanged', onLoadSingleGamePage);
