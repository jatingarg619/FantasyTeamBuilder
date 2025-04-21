const FantasyTeamBuilder = require('./fantasy_builder');

async function testFantasyBuilder() {
    try {
        // Replace these with your actual API keys for testing
        const firecrawlKey = process.env.FIRECRAWL_API_KEY || 'your_firecrawl_key';
        const geminiKey = process.env.GEMINI_API_KEY || 'your_gemini_key';

        console.log('Creating FantasyTeamBuilder instance...');
        const builder = new FantasyTeamBuilder(firecrawlKey, geminiKey);

        console.log('Fetching data from Cricbuzz and ESPNCricinfo...');
        const data = await builder.getData();

        console.log('\nTeam Selection Results:');
        console.log('------------------------');
        
        console.log('\nStrategy:');
        console.log(data.strategy_explanation);

        console.log('\nCaptain:', data.captain.name);
        console.log('Reason:', data.captain.reason);

        console.log('\nVice Captain:', data.vice_captain.name);
        console.log('Reason:', data.vice_captain.reason);

        console.log('\nSelected Players:');
        data.players.forEach(player => {
            console.log(`\n${player.name} (${player.role})`);
            console.log(`Reason: ${player.reason}`);
        });

    } catch (error) {
        console.error('Error:', error.message);
    }
}

testFantasyBuilder();
