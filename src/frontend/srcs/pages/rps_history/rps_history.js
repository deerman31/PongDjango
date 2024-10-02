async function fetchRpsResults() {
    let username;
    const accessToken = await verifyAndFetchToken();
    if (!accessToken) { return; }
    try {
        let response = await fetch('/api/get/name/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "アクセスに問題があります。ログインし直してください。");
        }
        const data = await response.json();
        if (data) {
            username = data.name;
        }
    } catch (error) {
        alert(error.message);
        window.location.href = '/';
        return;
    }


    const response = await fetch('/api/rps_game_result/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${accessToken}`
        }
    });

    if (response.ok) {
        const data = await response.json();
        displayRpsGameResults(data.results, username);
    } else {
        console.error('Failed to fetch game results');
    }
}

function displayRpsGameResults(results, username) {
    const resultsTableBody = document.getElementById('resultsTableBody');
    let wins = 0;
    let losses = 0;

    results.forEach(result => {
        if (result.winner === username) {
            wins += 1;
        } else if (result.loser === username) {
            losses += 1;
        }

        const row = document.createElement('tr');
        row.appendChild(createTdElement(result.date_time));
        row.appendChild(createTdElement(result.winner));
        row.appendChild(createTdElement(result.winner_score));
        row.appendChild(createTdElement(result.loser));
        row.appendChild(createTdElement(result.loser_score));
        resultsTableBody.appendChild(row);
    });

    const totalGames = wins + losses;
    let winRate = 0;
    if (totalGames > 0) {
        winRate = (wins / totalGames) * 100;
    }

    document.getElementById('wins').innerText = wins;
    document.getElementById('losses').innerText = losses;
    document.getElementById('win_rate').innerText = winRate.toFixed(2) + '%';
}

async function onLoadRPSHistoryPage(event) {
    if (event.detail !== '#/rps_history') {
        return;
    }

    fetchRpsResults();
}
window.removeEventListener('ftPageChanged', onLoadRPSHistoryPage);
window.addEventListener('ftPageChanged', onLoadRPSHistoryPage);
