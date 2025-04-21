"""
Flask API for Fantasy Cricket Team Builder
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from google import genai
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from backend.utils.scraper import FirecrawlScraper
from backend.config.firecrawl_config import FIRECRAWL_CONFIG

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logger.info("Flask app initialized with CORS")

# Get API keys from environment
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable is not set")
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)
logger.info("Gemini client initialized")

@app.route('/api/scrape', methods=['POST'])
def scrape():
    try:
        logger.info("[API HIT] /api/scrape endpoint called")
        data = request.json
        url = data.get('url')
        options = data.get('options', {})
        logger.info(f"[API HIT] Scraping URL: {url}")
        logger.debug(f"Scrape options: {options}")
        if not url:
            logger.error("Missing URL in request")
            return jsonify({'error': 'URL is required'}), 400
        logger.info("Calling FirecrawlScraper.scrape_url()")
        scraper = FirecrawlScraper()
        scraped_data = scraper.scrape_url(url, options)
        logger.info("Returning scraped data to client")
        return jsonify(scraped_data)
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/gemini', methods=['POST'])
def gemini():
    try:
        logger.info("[API HIT] /api/gemini endpoint called")
        data = request.json
        mode = data.get('mode')
        html_content = data.get('html_content')
        user_query = data.get('user_query', '')
        logger.info(f"[API HIT] Gemini mode: {mode}")
        logger.debug(f"User query: {user_query}")
        if not html_content or not mode:
            logger.error("Missing html_content or mode in request")
            return jsonify({'error': 'html_content and mode are required'}), 400

        if mode == 'extract_matches':
            prompt = (
                "Given the following HTML content of the Cricbuzz homepage and the user query, return the single best match URL for today's live or upcoming matches that matches the query. "
                "Return only the URL as a plain string (not JSON or array).\n"
                f"User Query: {user_query}\n"
                f"HTML:\n{html_content}"
            )
            logger.info("Prompting Gemini to extract the best match URL from homepage HTML")
            response = client.models.generate_content(
                model="gemini-2.5-pro-preview-03-25",
                contents=prompt
            )
            logger.debug(f"Gemini response: {response.text}")
            return jsonify({'match_url': response.text.strip()})

        elif mode == 'build_team':
            prompt = (
                "Given the following HTML content of a Cricbuzz match page and the user query, build an optimal fantasy cricket team for the match. "
                "Return the team as a JSON object with player names and roles.\n"
                f"User Query: {user_query}\n"
                f"Match Page HTML:\n{html_content}"
            )
            logger.info("Prompting Gemini to build fantasy team from match page HTML and user query")
            response = client.models.generate_content(
                model="gemini-2.5-pro-preview-03-25",
                contents=prompt
            )
            logger.debug(f"Gemini response: {response.text}")
            return jsonify({'team': response.text})

        else:
            logger.error(f"Unknown mode: {mode}")
            return jsonify({'error': 'Unknown mode'}), 400
    except Exception as e:
        logger.error(f"Error in Gemini endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def extract_json_from_text(text):
    """Extract JSON from text that might contain additional content."""
    # Clean the text first
    text = text.strip()
    
    # Try to find JSON within markdown code blocks
    if "```" in text:
        # Try to find JSON code block
        blocks = text.split("```")
        for block in blocks:
            if block.strip().startswith(("json\n", "{\n", "{")):
                text = block.replace("json\n", "").strip()
                break
    
    # Find the first { and last } to extract potential JSON
    start = text.find("{")
    end = text.rfind("}") + 1
    
    if start != -1 and end != 0:
        return text[start:end]
    return text

def validate_team_json(data):
    """Validate the team JSON structure and content."""
    required_fields = {"captain", "players", "strategy"}
    if not isinstance(data, dict):
        raise ValueError("Response is not a dictionary")
    
    # Check required fields
    if not all(field in data for field in required_fields):
        raise ValueError(f"Missing required fields. Required: {required_fields}")
    
    # Validate players list
    if not isinstance(data["players"], list):
        raise ValueError("Players must be a list")
    
    if len(data["players"]) != 11:
        raise ValueError(f"Must have exactly 11 players, got {len(data['players'])}")
    
    # Validate captain is in players list
    if data["captain"] not in data["players"]:
        raise ValueError("Captain must be one of the selected players")
    
    # Validate all fields are strings
    if not isinstance(data["captain"], str) or not isinstance(data["strategy"], str):
        raise ValueError("Captain and strategy must be strings")
    
    if not all(isinstance(p, str) for p in data["players"]):
        raise ValueError("All player names must be strings")
    
    return True

def clean_url(url):
    """Clean and validate a Cricbuzz URL."""
    # Remove any markdown formatting
    url = url.replace('`', '').strip()
    
    # Remove any text before or after the URL
    if 'https://www.cricbuzz.com' in url:
        start = url.find('https://www.cricbuzz.com')
        end = url.find('\n', start) if url.find('\n', start) != -1 else len(url)
        url = url[start:end].strip()
    
    return url

@app.route('/build-team', methods=['POST'])
def build_team():
    try:
        logger.info("API hit: /build-team")
        data = request.get_json()
        
        # Validate input
        if not data or 'team1' not in data or 'team2' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        team1 = data['team1']
        team2 = data['team2']
        logger.info(f"Finding match for teams: {team1} vs {team2}")

        # Step 1: Scrape Cricbuzz homepage
        try:
            scraper = FirecrawlScraper()
            cricbuzz_url = "https://www.cricbuzz.com"
            logger.info("Scraping Cricbuzz homepage...")
            homepage_data = scraper.scrape_url(cricbuzz_url, {})
            logger.info("Successfully scraped homepage")
        except Exception as e:
            logger.error(f"Error scraping Cricbuzz homepage: {str(e)}")
            return jsonify({'error': 'Failed to scrape Cricbuzz homepage'}), 500

        # Step 2: Find match URL using Gemini
        url_prompt = f"""Find the IPL 2024 match URL between {team1} and {team2} from this Cricbuzz homepage data.
Look for URLs containing the team abbreviations (like kkrvgt, rcbvmi, etc).
Return ONLY the complete URL starting with 'https://www.cricbuzz.com/'.
Do not include any markdown formatting, quotes, or additional text.

Homepage Data:
{json.dumps(homepage_data, indent=2)}"""

        logger.info("Getting match URL from Gemini...")
        url_response = client.models.generate_content(
            model="gemini-2.5-pro-preview-03-25",
            contents=url_prompt
        )
        
        # Clean and validate the URL
        match_url = clean_url(url_response.text)
        logger.info(f"Raw URL from Gemini: {url_response.text}")
        logger.info(f"Cleaned URL: {match_url}")
        
        if not match_url:
            return jsonify({'error': 'Could not find match URL'}), 404
            
        # Ensure URL starts with https://www.cricbuzz.com
        if not match_url.startswith('https://www.cricbuzz.com'):
            if match_url.startswith('/'):
                match_url = f"https://www.cricbuzz.com{match_url}"
            else:
                match_url = f"https://www.cricbuzz.com/{match_url}"
                
        logger.info(f"Final formatted match URL: {match_url}")

        # Validate URL format
        if not match_url.startswith('https://www.cricbuzz.com/') or ' ' in match_url:
            logger.error(f"Invalid URL format: {match_url}")
            return jsonify({'error': 'Invalid match URL format'}), 400

        # Step 3: Scrape match data using FirecrawlScraper
        try:
            logger.info(f"Scraping match data from URL: {match_url}")
            match_data = scraper.scrape_url(match_url, {})
            if not match_data:
                logger.error("No match data returned from scraper")
                return jsonify({'error': 'No match data found'}), 404
            logger.info(f"Successfully scraped match data: {json.dumps(match_data, indent=2)}")
        except Exception as e:
            logger.error(f"Error scraping match data: {str(e)}")
            return jsonify({'error': f'Failed to scrape match data: {str(e)}'}), 500

        # Step 4: Get match analysis from Gemini
        analysis_prompt = f"""Analyze this cricket match data and provide key insights for fantasy team selection.
Focus on player performance, pitch conditions, and match context.

Match Data:
{json.dumps(match_data, indent=2)}

Return ONLY the analysis, no additional formatting."""

        logger.info("Getting match analysis from Gemini...")
        analysis_response = client.models.generate_content(
            model="gemini-2.5-pro-preview-03-25",
            contents=analysis_prompt
        )
        match_analysis = analysis_response.text.strip()
        logger.info(f"Match analysis: {match_analysis}")

        # Step 5: Build fantasy team based on the analysis
        team_prompt = f"""Create a fantasy cricket team based on this match analysis and available players from the match data.
Return ONLY a valid JSON object with no additional text.

Match Analysis:
{match_analysis}

Match Data (for player selection):
{json.dumps(match_data, indent=2)}

Required JSON format:
{{
    "captain": "PLAYER_NAME",
    "players": ["PLAYER_1", "PLAYER_2", "PLAYER_3", "PLAYER_4", "PLAYER_5", "PLAYER_6", "PLAYER_7", "PLAYER_8", "PLAYER_9", "PLAYER_10", "PLAYER_11"],
    "strategy": "Brief strategy explanation"
}}

Rules:
1. Select exactly 11 players from the available players in the match data
2. Captain must be one of the selected players
3. Return ONLY the JSON object, no other text"""

        logger.info("Building fantasy team based on analysis...")
        team_response = client.models.generate_content(
            model="gemini-2.5-pro-preview-03-25",
            contents=team_prompt
        )
        
        logger.info(f"Raw Gemini team response: {team_response.text}")
        
        try:
            # Parse and validate the team JSON
            result = json.loads(extract_json_from_text(team_response.text))
            validate_team_json(result)
            logger.info(f"Successfully validated team JSON: {json.dumps(result, indent=2)}")
            
            # Add the match analysis and URL to the response
            result['match_analysis'] = match_analysis
            result['match_url'] = match_url
            return jsonify(result)
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse or validate Gemini response: {str(e)}")
            logger.error(f"Response that failed to parse: {team_response.text}")
            return jsonify({'error': 'Failed to generate valid team'}), 500
            
    except Exception as e:
        logger.error(f"Error in /build-team: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=3000, debug=True)
