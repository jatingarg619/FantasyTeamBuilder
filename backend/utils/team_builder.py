from typing import Dict, List, Any
import openai
import os
from backend.config.firecrawl_config import FANTASY_CONFIG, SCORING_CONFIG

class TeamBuilderAgent:
    def __init__(self):
        self.config = FANTASY_CONFIG
        self.max_credits = self.config['max_credits']
        self.team_size = self.config['team_size']
        self.max_per_team = self.config['max_per_team']
        self.role_constraints = self.config['role_constraints']
        self.scoring_config = SCORING_CONFIG

    def validate_team_constraints(self, team: List[Dict]) -> bool:
        """
        Validate if team meets all constraints
        """
        if len(team) != self.team_size:
            return False
            
        total_credits = sum(player['credits'] for player in team)
        if total_credits > self.max_credits:
            return False

        # Check team distribution
        team_counts = {}
        for player in team:
            team_counts[player['team']] = team_counts.get(player['team'], 0) + 1
            if team_counts[player['team']] > self.max_per_team:
                return False

        # Check role constraints
        role_counts = {}
        for player in team:
            role_counts[player['role']] = role_counts.get(player['role'], 0) + 1
        
        for role, (min_count, max_count) in self.role_constraints.items():
            if role_counts.get(role, 0) < min_count or role_counts.get(role, 0) > max_count:
                return False

        return True

    def calculate_player_score(self, match_stats: Dict) -> float:
        """
        Calculate player score based on match statistics
        """
        score = 0
        
        # Batting points
        runs = match_stats.get('runs', 0)
        score += runs * self.scoring_config['batting']['run']
        score += match_stats.get('fours', 0) * self.scoring_config['batting']['four']
        score += match_stats.get('sixes', 0) * self.scoring_config['batting']['six']
        
        if runs >= 100:
            score += self.scoring_config['batting']['hundred']
        elif runs >= 50:
            score += self.scoring_config['batting']['fifty']
            
        # Bowling points
        wickets = match_stats.get('wickets', 0)
        score += wickets * self.scoring_config['bowling']['wicket']
        score += match_stats.get('maidens', 0) * self.scoring_config['bowling']['maiden']
        
        if wickets >= 5:
            score += self.scoring_config['bowling']['five_wickets']
        elif wickets >= 4:
            score += self.scoring_config['bowling']['four_wickets']
            
        # Fielding points
        score += match_stats.get('catches', 0) * self.scoring_config['fielding']['catch']
        score += match_stats.get('stumpings', 0) * self.scoring_config['fielding']['stumping']
        score += match_stats.get('run_outs', 0) * self.scoring_config['fielding']['run_out']
        
        return score

    def select_captain_vice_captain(self, team: List[Dict]) -> tuple:
        """
        Select captain and vice-captain based on form
        """
        # Sort by form and return top 2 players
        sorted_team = sorted(team, key=lambda x: sum(x.get('last_3_matches', [0])), reverse=True)
        return sorted_team[0], sorted_team[1]

def build_fantasy_team(match_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to build fantasy team
    """
    agent = TeamBuilderAgent()
    
    # TODO: Implement actual team building logic using LLM
    # For now, return a mock team
    mock_team = {
        "players": match_data['players'][:11],  # First 11 players
        "captain": match_data['players'][0],     # Best player as captain
        "vice_captain": match_data['players'][1],# Second best as VC
        "total_credits": 95.5,
        "timestamp": "2025-04-18T13:00:00Z"
    }
    
    return mock_team
