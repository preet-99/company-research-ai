# AI Company Research Assistant

An AI-powered web application that researches any company and generates a professional PDF report automatically.

## Features

- Supports company name or website URL as input
- Automatically crawls the company website
- Uses Serper.dev for web search and research
- Uses OpenRouter for AI-powered analysis
- Generates company summary, products, pain points, and competitors
- Downloads a professional PDF report
- ChatGPT-style chat interface
- AI model selector

## Tech Stack

- Python
- Streamlit
- BeautifulSoup (web crawling)
- Serper.dev (search API)
- OpenRouter (AI API)
- ReportLab (PDF generation)

## Setup Instructions

### 1. Clone the repository

git clone https://github.com/preet-99/company-research-ai.git
cd company-research-ai

### 2. Install dependencies

pip install -r requirements.txt

### 3. Set up environment variables

Create a .streamlit/secrets.toml file:

SERPER_API_KEY = "your_serper_api_key"
OPENROUTER_API_KEY = "your_openrouter_api_key"

### 4. Run the application

streamlit run app.py

## Deployment

This application is deployed on Streamlit Cloud.

Live URL: your_deployed_url_here

## Environment Variables

| Variable | Description |
|----------|-------------|
| SERPER_API_KEY | API key from serper.dev |
| OPENROUTER_API_KEY | API key from openrouter.ai |

## Project Structure

```
company-research-ai/
├── .streamlit/
│   └── secrets.toml
├── .gitignore
├── app.py
├── search.py
├── crawler.py
├── ai_processor.py
├── pdf_generator.py
├── requirements.txt
└── README.md
```

## How It Works

1. User enters a company name or website URL
2. Serper.dev searches for the official website and company info
3. The crawler visits and extracts content from important pages
4. OpenRouter AI analyzes the collected data
5. A professional PDF report is generated
6. Results are displayed in a ChatGPT-style interface



