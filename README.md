# Fantasy Cricket Team Builder

An AI-powered fantasy cricket team builder that uses Google's Gemini 2.5 Pro model to analyze match data and create optimal teams.

## Features

- Real-time match data scraping from Cricbuzz
- AI-powered match analysis using Gemini 2.5 Pro
- Dynamic team building based on current form and conditions
- Automatic match URL detection based on team selection
- Detailed match analysis and strategy explanation

## Requirements

- Python 3.8+
- Flask
- Google Generative AI SDK
- FirecrawlScraper
- Environment variables for API keys

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Running the Application

1. Start the backend server:
```bash
cd backend
python app.py
```
The server will start on `http://localhost:3000`

2. Load the Chrome extension:
- Open Chrome and go to `chrome://extensions/`
- Enable "Developer mode"
- Click "Load unpacked" and select the `extension` directory

## API Endpoints

### POST /build-team
Builds a fantasy team for a match between two teams.

Request body:
```json
{
    "team1": "KKR",
    "team2": "GT"
}
```

Response:
```json
{
    "captain": "Player Name",
    "players": ["Player 1", "Player 2", ...],
    "strategy": "Strategy explanation",
    "match_analysis": "Detailed match analysis",
    "match_url": "Cricbuzz match URL"
}
```

### GET /health
Health check endpoint to verify server status.

## Error Handling

The API includes comprehensive error handling for:
- Invalid team names
- Match URL not found
- Scraping failures
- Invalid responses from Gemini
- JSON parsing errors

## Development

- Backend code is in the `backend/` directory
- Chrome extension code is in the `extension/` directory
- Environment variables are managed through `.env` files
- Logs are available in the console when running the server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
