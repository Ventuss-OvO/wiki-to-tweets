# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a toolings repository for "mosumosu" containing various utility scripts and tools. Currently contains:

- **ai-script**: A CLI tool for generating text using Google Vertex AI (Gemini 2.5 Flash model)

## ai-script Tool

### Setup and Running

The ai-script requires a Google Cloud service account credential file:

```bash
# 1. Copy credential.json file to ai-script folder
# 2. Install dependencies and run
cd ai-script
npm i
npm run start                    # Default prompt: "hello. how are you"
npm run start "your prompt"      # Custom prompt
```

### Architecture

- **Technology**: Node.js ES modules using Vercel AI SDK (@ai-sdk/google-vertex)
- **Location**: asia-northeast1
- **Model**: gemini-2.5-flash
- **Main file**: ai-script/index.js

The script:
1. Reads Google Cloud credentials from `credential.json` (contains `project_id`)
2. Creates a Vertex AI client instance
3. Accepts prompt from command line arguments (argv[2])
4. Calls Vertex AI's `generateText()` function
5. Outputs the generated text or helpful error messages

### Dependencies

- `@ai-sdk/google-vertex`: Vercel AI SDK provider for Google Vertex AI
- `@ai-sdk/google`: Google AI SDK integration
- `ai`: Vercel AI SDK core library

### Important Notes

- Requires Vertex AI API to be enabled in Google Cloud project
- credential.json must contain valid service account credentials with `project_id`
- The script includes helpful error handling for 404 errors (API not enabled)
