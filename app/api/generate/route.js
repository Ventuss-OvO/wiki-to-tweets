import { NextResponse } from 'next/server'
import { generateText } from 'ai'
import { createVertex } from '@ai-sdk/google-vertex'
import { readFileSync, existsSync } from 'fs'

// 加载 credential
const credentialPath = '/Users/jason/Downloads/workflow/llm-api/ai-script/credential.json'

let vertex = null

if (existsSync(credentialPath)) {
    try {
        const credentials = JSON.parse(readFileSync(credentialPath, 'utf-8'))
        process.env.GOOGLE_APPLICATION_CREDENTIALS = credentialPath

        vertex = createVertex({
            project: credentials.project_id,
            location: 'asia-northeast1'
        })
        console.log('✅ Loaded credentials from:', credentialPath)
    } catch (e) {
        console.error('❌ Failed to load credentials:', e.message)
    }
} else {
    console.error('❌ Credential file not found:', credentialPath)
}

export async function POST(request) {
    try {
        const { htmlContent, prompt } = await request.json()

        if (!htmlContent) {
            return NextResponse.json({ error: '缺少 HTML 内容' }, { status: 400 })
        }

        if (!vertex) {
            return NextResponse.json({
                error: 'Gemini API 未配置，请检查 credential.json',
                success: false
            }, { status: 500 })
        }

        // 直接把 HTML 内容和 Prompt 发给 LLM
        const finalPrompt = prompt.replace('{html_content}', htmlContent)

        console.log('📤 Calling Gemini API...')
        console.log('Prompt length:', finalPrompt.length)

        const { text } = await generateText({
            model: vertex('gemini-2.5-flash'),
            prompt: finalPrompt,
            maxTokens: 8192,
        })

        console.log('✅ Gemini response received, length:', text.length)

        // 按 "---" 分割成多条推文
        const tweets = text.split('---').map(t => t.trim()).filter(t => t)

        return NextResponse.json({
            success: true,
            tweets,
            raw_response: text
        })

    } catch (error) {
        console.error('❌ Generate error:', error.message)
        return NextResponse.json({
            error: error.message,
            success: false
        }, { status: 500 })
    }
}
