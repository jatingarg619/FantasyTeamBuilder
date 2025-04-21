# Fantasy Team Builder Agent - IPL 2025

A Chrome Extension that uses LLM + web data to generate optimized IPL fantasy teams based on natural language input.

## Features

- Natural language team building requests
- Real-time match & player data extraction
- Intelligent team composition with role constraints
- Captain/Vice-captain selection
- Dream11-style credit system

## Project Structure

```
assignment24/
├── extension/           # Chrome Extension files
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   └── styles.css
├── backend/            # Backend API server
│   ├── app.py
│   ├── requirements.txt
│   └── utils/
│       ├── scraper.py
│       └── team_builder.py
└── data/              # Sample data and schemas
    └── player_data.json
```

## Setup Instructions

1. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Load Chrome Extension:
   - Open Chrome
   - Go to chrome://extensions/
   - Enable Developer Mode
   - Click "Load unpacked"
   - Select the `extension` folder

## Tech Stack

- Frontend: HTML, CSS, JavaScript (Chrome Extension)
- Backend: Python Flask/FastAPI
- LLM: GPT-4/Gemini API
- Data: Web scraping + Static JSON
- Optional: Telegram Bot integration

## Development Timeline

- Day 1: Data format + team rules
- Day 2: Mock JSON + scraping logic
- Day 3: LLM prompt & backend agent
- Day 4: Chrome Extension UI
- Day 5: Testing + Demo
# FantasyTeamBuilder
