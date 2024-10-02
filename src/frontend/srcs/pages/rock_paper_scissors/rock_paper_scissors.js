async function rcsRoomIn() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    const wsUrl = `ws/rock_paper_scissors/?token=${accessToken}`;
    window.socket = new WebSocket(wsUrl);

    window.socket.onopen = function(e) {
        console.log('WebSocket connection opened:', event);
        document.getElementById('game-status').textContent = 'ゲームの準備ができました。';
    };

    window.socket.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.type === 'start_game') {
            document.getElementById('game-status').textContent = 'じゃんけんを始めます！';
        } else if (data.type === 'game_state') {
            updateGameState(JSON.parse(data.message));
        } else if (data.type === 'game_end') {
            document.getElementById('game-status').textContent = 'ゲーム終了！';
            document.getElementById('game-result').textContent = '勝者: ' + (data.winner || '引き分け');
            safeCloseRpsGameWebSocket(1000, 'finish')
            window.location.hash = '#/home';
        }
    };

    window.socket.onclose = function(event) {
        console.log('WebSocket closed:', event);
        if (event.wasClean) {
            document.getElementById('game-status').textContent = '接続がクリーンに閉じられました。';
        } else {
            document.getElementById('game-status').textContent = '接続が切断されました。';
        }
        if (window.socket) {
            window.socket = null;
        }
    };
    window.socket.onerror = function(event) {
        console.error('WebSocket error:', event);
    };
}

function sendHand(hand) {
    window.socket.send(JSON.stringify({
        action: 'Hands',
        hand: hand
    }));
}

function updateGameState(gameState) {
    document.getElementById('player1-name').textContent = gameState.player1;
    document.getElementById('player1-score').textContent = gameState.player1_score;
    document.getElementById('player1-hand').textContent = translateHand(gameState.player1_hand);

    document.getElementById('player2-name').textContent = gameState.player2;
    document.getElementById('player2-score').textContent = gameState.player2_score;
    document.getElementById('player2-hand').textContent = translateHand(gameState.player2_hand);
}

function translateHand(hand) {
    switch(hand) {
        case 'rock':
            return 'グー';
        case 'paper':
            return 'パー';
        case 'scissors':
            return 'チョキ';
        default:
            return '未選択';
    }
}

function safeCloseRpsGameWebSocket(code, reason) {
    window.removeEventListener('hashchange', rcsHandleHashchange);
    window.removeEventListener('beforeunload', rcsHandleBeforeunload);
    window.removeEventListener('popstate', rcsHandlePopstate);
    if (window.socket && window.socket.readyState === WebSocket.OPEN) {
        window.socket.close(code, reason);
        window.socket = null; // WebSocket を解放する
    }
}

function rcsHandleHashchange(event) {
    console.log("hashchange")
    safeCloseRpsGameWebSocket(4003, "hashchange");
}
function rcsHandleBeforeunload(event) {
    console.log("beforeunload")
    safeCloseRpsGameWebSocket(4002, "beforeunload");
}
function rcsHandlePopstate(event) {
    console.log("popstate")
    safeCloseRpsGameWebSocket(4001, "popstate");
}

async function onLoadRPSPage(event) {
    if (event.detail !== '#/rock_paper_scissors') {
        return;
    }

    // codeは適当
    safeCloseRpsGameWebSocket(4000, "load");

    window.addEventListener('hashchange', rcsHandleHashchange);
    window.addEventListener('beforeunload', rcsHandleBeforeunload);
    window.addEventListener('popstate', rcsHandlePopstate);
    rcsRoomIn();
}
window.removeEventListener('ftPageChanged', onLoadRPSPage);
window.addEventListener('ftPageChanged', onLoadRPSPage);

