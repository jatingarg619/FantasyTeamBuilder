document.addEventListener('DOMContentLoaded', function() {
    console.log('Popup loaded');
    
    const team1Select = document.getElementById('team1');
    const team2Select = document.getElementById('team2');
    const buildButton = document.getElementById('build-team');
    const resultsSection = document.getElementById('results');
    const errorSection = document.getElementById('error');
    const loadingSection = document.getElementById('loading');
    const teamOutput = document.getElementById('team-output');
    const matchUrlOutput = document.getElementById('match-url-output');
    const loadingMsg = document.getElementById('loading-msg');

    if (!team1Select || !team2Select || !buildButton || !resultsSection || !errorSection || !loadingSection || !teamOutput || !matchUrlOutput || !loadingMsg) {
        console.error('Required elements not found');
        return;
    }

    function showLoading() {
        loadingSection.style.display = 'block';
        errorSection.style.display = 'none';
        resultsSection.style.display = 'none';
        buildButton.disabled = true;
    }

    function hideLoading() {
        loadingSection.style.display = 'none';
        buildButton.disabled = false;
    }

    function showError(message) {
        console.error('Showing error:', message);
        errorSection.textContent = message;
        errorSection.style.display = 'block';
        resultsSection.style.display = 'none';
    }

    function displayResults(data) {
        resultsSection.style.display = 'block';
        errorSection.style.display = 'none';

        // Create HTML for results
        let html = '<h3>Your Fantasy Team</h3>';
        
        // Display captain
        html += '<div class="captain-section">';
        html += `<p><strong>Captain:</strong> ${data.captain}</p>`;
        html += '</div>';

        // Display all players
        html += '<div class="players-section">';
        html += '<h4>Team Composition</h4>';
        html += '<ul>';
        data.players.forEach(player => {
            html += `<li>${player}</li>`;
        });
        html += '</ul>';
        html += '</div>';

        // Display strategy
        html += '<div class="strategy-section">';
        html += '<h4>Team Strategy</h4>';
        html += `<p>${data.strategy}</p>`;
        html += '</div>';

        resultsSection.innerHTML = html;
    }

    buildButton.addEventListener('click', async function() {
        const team1 = team1Select.value;
        const team2 = team2Select.value;

        if (!team1 || !team2 || team1 === "Select Team 1" || team2 === "Select Team 2") {
            showError('Please select both teams');
            return;
        }

        if (team1 === team2) {
            showError('Please select different teams');
            return;
        }

        showLoading();

        try {
            const response = await fetch('http://localhost:3000/build-team', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    team1: team1,
                    team2: team2
                })
            });

            if (!response.ok) {
                throw new Error('Failed to build team');
            }

            const data = await response.json();
            hideLoading();
            displayResults(data);
        } catch (error) {
            hideLoading();
            showError('Error building team: ' + error.message);
        }
    });
});
