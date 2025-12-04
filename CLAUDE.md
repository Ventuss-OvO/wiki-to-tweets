# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wiki-to-Tweets generator for Hinatazaka46 (日向坂46) Fandom Wiki pages. Parses HTML wiki pages and uses AI to generate Twitter-style posts about idol group members.

## Architecture

Three main components:

1. **Python CLI** (`wiki_to_tweets.py`, `run.py`) - Main processing tool
   - Parses Fandom Wiki HTML files using BeautifulSoup
   - Extracts member profiles from `<aside class="portable-infobox">` elements
   - AI backend priority: Gemini (Node.js) → Gemini (REST) → Claude → OpenAI → Ollama → template fallback
   - Outputs to `tweets_output.json`

2. **Node.js AI Script** (`llm-api/ai-script/`) - Gemini API wrapper
   - Uses Vercel AI SDK (`@ai-sdk/google-vertex`) with `gemini-2.5-flash` model
   - Called via subprocess from Python CLI (hardcoded path: `/Users/jason/Downloads/workflow/llm-api/ai-script`)
   - Requires `credential.json` (Google Cloud service account)

3. **Next.js Web App** (`web/`) - Web interface
   - Drag-and-drop HTML upload with batch processing
   - Customizable prompts with `{html_content}` placeholder
   - Uses cheerio for HTML parsing client-side
   - API route at `/api/generate` calls Gemini directly

## Commands

```bash
# Python CLI - Interactive mode
python3 run.py

# Python CLI - Direct commands
python3 wiki_to_tweets.py --preview          # Preview parsed data
python3 wiki_to_tweets.py ./info             # Process info directory
python3 wiki_to_tweets.py --single "x.html"  # Single file
python3 wiki_to_tweets.py -o custom.json     # Custom output filename

# Node.js AI script (standalone)
cd llm-api/ai-script && npm i
npm run start "your prompt"

# Web app
cd web && npm i
npm run dev    # Development server at localhost:3000
npm run build  # Production build
```

## Configuration

- **Gemini credentials**: Place `credential.json` (Google Cloud service account) in `llm-api/ai-script/`
- **Alternative AI backends**: Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` environment variables
- **Vercel deployment**: Set `GOOGLE_PROJECT_ID`, `GOOGLE_CLIENT_EMAIL`, `GOOGLE_PRIVATE_KEY` env vars

## Key Files

- `wiki_to_tweets.py:36` - `parse_wiki_html()` extracts member data from infobox
- `wiki_to_tweets.py:232` - `generate_tweets_with_ai()` AI backend selection logic
- `web/app/api/generate/route.js:53` - Next.js POST endpoint for Gemini generation
- `web/app/page.js:5` - Default prompt template with tweet requirements
