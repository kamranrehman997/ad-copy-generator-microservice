# E-Commerce Ad Copy Generator Microservice

A FastAPI microservice that generates structured marketing ad copy variations using Claude and the Anthropic API.

## Features
- Generates 4 distinct marketing angles: Pain Point, Social Proof, Feature Focus, Urgency.
- Validates data inputs and outputs structured JSON schemas.
- Built with FastAPI, Uvicorn, and anthropic.

## Local Setup

1. Clone the repository:
   git clone <YOUR_GITHUB_REPO_URL>
   cd ad-copy-microservice

2. Activate virtual environment:
   .\venv\Scripts\Activate.ps1

3. Install dependencies:
   pip install -r requirements.txt

4. Run the server:
   python -m uvicorn app.main:app --reload
