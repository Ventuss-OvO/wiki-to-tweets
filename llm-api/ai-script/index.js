import { generateText } from 'ai'
import { readFileSync } from 'fs'
import { createVertex } from '@ai-sdk/google-vertex'

const credentials = JSON.parse(readFileSync('./credential.json', 'utf-8'))

// Set the path to credentials file
process.env.GOOGLE_APPLICATION_CREDENTIALS = './credential.json'

// Create Vertex AI provider
const vertex = createVertex({
    project: credentials.project_id,
    location: 'asia-northeast1'
})

const prompt = process.argv[2] || 'hello. how are you'

try {
    const { text } = await generateText({
        model: vertex('gemini-2.5-flash'),
        prompt,
    })
    console.log(text)
} catch (error) {
    console.error('Error:', error.message)
    if (error.statusCode === 404) {
        console.log('\nTo fix this:')
        console.log('1. Enable the Vertex AI API in your Google Cloud project:')
        console.log(
            '   https://console.cloud.google.com/apis/library/aiplatform.googleapis.com',
        )
        console.log(
            '2. Or run: gcloud services enable aiplatform.googleapis.com --project=iceberg-476707',
        )
    }
}
