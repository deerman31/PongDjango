async function tournamentRoomIn() {
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }

    const wsUrl = `/ws/tournament/?token=${accessToken}`;
    window.roomSocket = new WebSocket(wsUrl);

    window.roomSocket.onopen = function(event) {
        console.log('WebSocket connection opened:', event);
    };

    window.roomSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // console.log('WebSocket message received:', data);

        if (data.message === 'Tournament is ready to start.') {
            document.getElementById('status-message').style.display = 'none';
            document.getElementById('move-btn-group').style.display = 'none';
            document.getElementById('tournament-container').style.display = 'table';

            const canvas = document.getElementById('pong-game');
            const ctx = canvas.getContext('2d');
            canvas.style.display = 'none';

            const bracket = JSON.parse(data.tournament_bracket);
            generateTournament(bracket);
            // トーナメント表示後にボタンを表示
            document.getElementById('ready-button').style.display = 'block';
        } else if (data.type === 'start_game') {
            document.getElementById('tournament-container').style.display = 'none';
            document.getElementById('ready-button').style.display = 'none';
            startTournamentPongGame();
        } else if (data.type === 'drawing') {
            let m = JSON.parse(data.message);
            updateTournamentPongGame(m);
        } else if (data.type === 'game_end') {
            const canvas = document.getElementById('pong-game');
            const ctx = canvas.getContext('2d');
            canvas.style.display = 'none';
            document.getElementById('status-message').style.display = 'block';
            document.getElementById('move-btn-group').style.display = 'none';

            document.getElementById('tournament-container').style.display = 'none';
            document.getElementById('ready-button').style.display = 'none';


        } else if (data.type === 'loser_gets_out') {
            // window.roomSocket.close(1000, 'loser');
            safeCloseTournamentWebSocket(1000, 'loser')
            window.location.hash = '#/home';
        } else if (data.type === 'victory') {
            // window.roomSocket.close(1000, 'victory');
            safeCloseTournamentWebSocket(1000, 'victory')
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

function onClickReadyButton(event) {
    if (window.roomSocket && window.roomSocket.readyState === WebSocket.OPEN) {
        window.roomSocket.send(JSON.stringify({ action: 'game_room_is_ready' }));
        console.log('"game_room_is_ready" message sent to the server.');
    }
}

function startTournamentPongGame() {
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

function updateTournamentPongGame(data) {
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
    // ctx.fillRect(780, data.player_2_y, 10, 100);
    ctx.fillRect(760, data.player_2_y, 10, 100);

    // ボール
    ctx.beginPath();
    ctx.arc(data.ball_x, data.ball_y, 10, 0, Math.PI * 2);
    ctx.fill();

    // スコア表示
    ctx.font = "30px Arial";
    ctx.fillText(data.score_1, 360, 50);
    ctx.fillText(data.score_2, 420, 50);
}


function generateTournament(data) {
    const container = document.getElementById('tournament-players');
    container.innerHTML = '';

    console.log("generateTournament", data);
    data.forEach((round, roundIndex) => {
        for (let i = 0; i < round.length / 2; ++i) {
            const playerA = round[(i * 2) + 0];
            const playerB = round[(i * 2) + 1];
            const tr = document.createElement('tr');
            tr.appendChild(createTdElement(playerA || 'TBD'));
            tr.appendChild(createTdElement(`Round ${roundIndex + 1}`));
            tr.appendChild(createTdElement(playerB || 'TBD'));
            container.appendChild(tr);
        }
    });
}

function onTournamentAction(action) {
    window.roomSocket.send(JSON.stringify({ action }));
}

function tournamentHandleKeyDown(event) {
    let action = null;
    //if (event.key === 'ArrowUp') {
    if (event.key === 'k') {
        onTournamentAction('up');
    //} else if (event.key === 'ArrowDown') {
    } else if (event.key === 'j') {
        onTournamentAction('down');
    }
    //console.log(action)
}
function safeCloseTournamentWebSocket(code, reason) {
    window.removeEventListener('keydown', tournamentHandleKeyDown);
    window.removeEventListener('hashchange', tournamentHandleHashchange);
    window.removeEventListener('beforeunload', tournamentHandleBeforeunload);
    window.removeEventListener('popstate', tournamentHandlePopstate);
    if (window.roomSocket && window.roomSocket.readyState === WebSocket.OPEN) {
        window.roomSocket.close(code, reason);
        window.roomSocket = null; // WebSocket を解放する
    }
}

function tournamentHandleHashchange(event) {
    console.log("hashchange")
    safeCloseTournamentWebSocket(4003, "hashchange");
}
function tournamentHandleBeforeunload(event) {
    console.log("beforeunload")
    safeCloseTournamentWebSocket(4002, "beforeunload");
}
function tournamentHandlePopstate(event) {
    console.log("popstate")
    safeCloseTournamentWebSocket(4001, "popstate");
}


async function onLoadTournamentWaitingPage(event) {
    if (event.detail !== '#/tournament_waiting') {
        return;
    }
    
    // codeは適当
    safeCloseTournamentWebSocket(4000, "load");

    tournamentRoomIn();
    window.addEventListener('keydown', tournamentHandleKeyDown);
    window.addEventListener('hashchange', tournamentHandleHashchange);
    window.addEventListener('beforeunload', tournamentHandleBeforeunload);
    window.addEventListener('popstate', tournamentHandlePopstate);
}
window.removeEventListener('ftPageChanged', onLoadTournamentWaitingPage);
window.addEventListener('ftPageChanged', onLoadTournamentWaitingPage);
