from utils.scraper import get_match_data
from utils.team_builder import build_fantasy_team

def test_specific_match():
    print("Testing Fantasy Team Builder for RCB vs PBKS...")
    
    try:
        # Test with specific match query
        query = "Build a fantasy team for RCB vs PBKS match"
        print(f"\nProcessing query: {query}")
        
        # Get match data
        match_data = get_match_data(query)
        
        print("\nMatch Information:")
        print(f"Teams: {match_data['match']['team1']} vs {match_data['match']['team2']}")
        print(f"Venue: {match_data['match']['venue']}")
        print(f"Date: {match_data['match']['date']}")
        
        print(f"\nPlayers found: {len(match_data['players'])}")
        print("\nSample players:")
        for player in match_data['players'][:5]:  # Show first 5 players
            print(f"\nName: {player['name']}")
            print(f"Team: {player['team']}")
            print(f"Role: {player['role']}")
            print(f"Credits: {player['credits']}")
            print(f"Form: {player['recent_form']}")
            print(f"Last 3 matches: {player['last_3_matches']}")
        
        # Build fantasy team
        team = build_fantasy_team(match_data)
        
        print("\nFantasy Team:")
        print(f"Captain: {team['captain']['name']} ({team['captain']['team']})")
        print(f"Vice Captain: {team['vice_captain']['name']} ({team['vice_captain']['team']})")
        print("\nTeam Composition:")
        for player in team['players']:
            print(f"- {player['name']} ({player['team']}) - {player['role']} - {player['credits']} credits")
        
        print(f"\nTotal Credits Used: {team['total_credits']}")
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")

if __name__ == "__main__":
    test_specific_match()
