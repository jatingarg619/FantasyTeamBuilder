class FirecrawlClient {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = 'http://localhost:3000';  // Match the Flask server URL
        console.log('FirecrawlClient initialized');
    }

    async scrapeUrl(url, options = {}) {
        console.log('Scraping URL:', url);
        try {
            const response = await fetch(`${this.baseUrl}/api/scrape`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify({
                    url,
                    ...options
                })
            });

            if (!response.ok) {
                const error = await response.text();
                console.error('Scraping failed:', error);
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Scraped data:', data);
            return data;
        } catch (error) {
            console.error('Scraping error:', error);
            throw new Error(`Scraping failed: ${error.message}`);
        }
    }
}

class FantasyTeamBuilder {
    constructor(firecrawlKey) {
        console.log('FantasyTeamBuilder initialized');
        this.firecrawlClient = new FirecrawlClient(firecrawlKey);
    }

    async getMatchData(query) {
        console.log('Getting match data for query:', query);
        try {
            // Extract team names from query
            const teams = this.extractTeams(query);
            console.log('Extracted teams:', teams);
            if (!teams || teams.length !== 2) {
                throw new Error('Could not identify two teams from the query');
            }

            // Get match details from Cricbuzz
            console.log('Fetching Cricbuzz data...');
            const matchData = await this.firecrawlClient.scrapeUrl(
                'cricbuzz.com',
                {
                    selectors: {
                        matches: '.cb-mtch-lst',
                        scores: '.cb-scr-wll-chvrn',
                        players: '.cb-player-list'
                    }
                }
            );

            // Get player stats from ESPNCricinfo
            console.log('Fetching ESPNCricinfo data...');
            const espnData = await this.firecrawlClient.scrapeUrl(
                'espncricinfo.com',
                {
                    selectors: {
                        stats: '.ds-w-full',
                        rankings: '.ds-table',
                        players: '.ds-flex'
                    }
                }
            );

            // Combine match and player data
            const combinedData = {
                match: matchData,
                espn: espnData,
                query: query,
                teams: teams
            };
            
            console.log('Combined data:', combinedData);
            return combinedData;
        } catch (error) {
            console.error('Error in getMatchData:', error);
            throw new Error(`Failed to get match data: ${error.message}`);
        }
    }

    async buildTeam(query) {
        console.log('Building team for query:', query);
        try {
            // Show loading state
            this.showLoading();

            // Get match and player data
            const cricketData = await this.getMatchData(query);
            console.log('Got cricket data:', cricketData);

            console.log('Sending data to backend for analysis...');
            // Send data to backend for Gemini processing
            const response = await fetch('http://localhost:3000/api/gemini', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cricket_data: JSON.stringify(cricketData, null, 2)
                })
            });

            if (!response.ok) {
                const error = await response.text();
                console.error('Backend error:', error);
                throw new Error(`Backend error: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Got result from backend:', result);
            
            if (result.error) {
                throw new Error(result.error);
            }

            // Parse and validate the team
            const team = JSON.parse(result.result);
            console.log('Parsed team:', team);
            
            this.validateTeam(team);
            console.log('Team validation passed');

            // Hide loading state
            this.hideLoading();

            return team;
        } catch (error) {
            console.error('Error in buildTeam:', error);
            this.hideLoading();
            throw new Error(`Team building failed: ${error.message}`);
        }
    }

    validateTeam(team) {
        console.log('Validating team:', team);
        // Validate team structure
        if (!team.captain || !team.vice_captain || !team.players) {
            throw new Error('Invalid team structure');
        }

        // Count player roles
        const roleCounts = {
            'wicket-keeper': 0,
            'batsman': 0,
            'bowler': 0,
            'all-rounder': 0
        };

        team.players.forEach(player => {
            if (!roleCounts[player.role.toLowerCase()]) {
                throw new Error(`Invalid player role: ${player.role}`);
            }
            roleCounts[player.role.toLowerCase()]++;
        });

        console.log('Role counts:', roleCounts);

        // Validate role counts
        if (roleCounts['wicket-keeper'] < 1 || roleCounts['wicket-keeper'] > 2) {
            throw new Error('Team must have 1-2 wicket-keepers');
        }
        if (roleCounts['batsman'] < 3 || roleCounts['batsman'] > 5) {
            throw new Error('Team must have 3-5 batsmen');
        }
        if (roleCounts['bowler'] < 3 || roleCounts['bowler'] > 5) {
            throw new Error('Team must have 3-5 bowlers');
        }
        if (roleCounts['all-rounder'] < 1 || roleCounts['all-rounder'] > 3) {
            throw new Error('Team must have 1-3 all-rounders');
        }
    }

    showLoading() {
        console.log('Showing loading state');
        const loading = document.querySelector('.loading');
        if (loading) loading.style.display = 'block';
    }

    hideLoading() {
        console.log('Hiding loading state');
        const loading = document.querySelector('.loading');
        if (loading) loading.style.display = 'none';
    }

    extractTeams(query) {
        console.log('Extracting teams from query:', query);
        // Common IPL team abbreviations
        const teams = {
            'RCB': 'Royal Challengers Bangalore',
            'CSK': 'Chennai Super Kings',
            'MI': 'Mumbai Indians',
            'KKR': 'Kolkata Knight Riders',
            'RR': 'Rajasthan Royals',
            'SRH': 'Sunrisers Hyderabad',
            'DC': 'Delhi Capitals',
            'PBKS': 'Punjab Kings',
            'GT': 'Gujarat Titans',
            'LSG': 'Lucknow Super Giants'
        };

        const matches = query.toUpperCase().match(/\b(RCB|CSK|MI|KKR|RR|SRH|DC|PBKS|GT|LSG)\b/g);
        console.log('Matched teams:', matches);
        return matches && matches.length === 2 ? matches : null;
    }
}

// Step 1: Scrape Cricbuzz homepage
async function getCricbuzzHomepage() {
    const response = await fetch('http://localhost:3000/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: 'https://www.cricbuzz.com' })
    });
    const data = await response.json();
    return data.data?.html || data.html || '';
}

// Step 2: Use Gemini to extract the best match URL for the query
async function getBestMatchUrlFromGemini(homepageHtml, userQuery) {
    const response = await fetch('http://localhost:3000/api/gemini', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            mode: 'extract_matches',
            html_content: homepageHtml,
            user_query: userQuery
        })
    });
    const data = await response.json();
    return data.match_url && typeof data.match_url === 'string' ? data.match_url.trim() : '';
}

// Step 3: Scrape selected match URL
async function getMatchPageHtml(matchUrl) {
    const response = await fetch('http://localhost:3000/api/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: matchUrl })
    });
    const data = await response.json();
    return data.data?.html || data.html || '';
}

// Step 4: Use Gemini to build the fantasy team
async function buildFantasyTeamWithGemini(matchHtml, userQuery) {
    const response = await fetch('http://localhost:3000/api/gemini', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            mode: 'build_team',
            html_content: matchHtml,
            user_query: userQuery
        })
    });
    const data = await response.json();
    return data.team;
}

// Expose the main flow for popup.js
export async function getTeamForUserQuery(userQuery) {
    // Step 1: Get Cricbuzz homepage HTML
    const homepageHtml = await getCricbuzzHomepage();
    // Step 2: Get the best match URL from Gemini
    const matchUrl = await getBestMatchUrlFromGemini(homepageHtml, userQuery);
    if (!matchUrl) {
        throw new Error('No match URL found for the given query.');
    }
    // Step 3: Scrape the selected match page
    const matchHtml = await getMatchPageHtml(matchUrl);
    // Step 4: Build the fantasy team with Gemini
    const team = await buildFantasyTeamWithGemini(matchHtml, userQuery);
    return { matchUrl, team };
}

// Make available globally for browser
window.FantasyTeamBuilder = FantasyTeamBuilder;
