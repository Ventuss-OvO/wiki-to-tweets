'use client'

import { useState, useRef } from 'react'

const DEFAULT_PROMPT = `你是一个专业的偶像粉丝账号运营者。我会给你一个 Fandom Wiki 页面的 HTML 内容，请根据其中的信息，生成 8-10 条 Twitter 风格的动态（推文）。

Wiki HTML 内容：
{html_content}

要求：
1. 每条推文不超过280字符（中文约140字）
2. 可以包含emoji，但不要过多
3. 风格要像真实的粉丝分享，有热情但不夸张
4. 推文类型要多样化，包括但不限于：
   - 成员基本介绍
   - 生日祝福模板
   - 昵称/外号趣事
   - 身高/星座/血型等冷知识
   - 出身地相关
   - 加入团体的经历
   - 鼓励应援的内容
   - 日常安利推荐
5. 使用中文撰写
6. 每条推文用 "---" 分隔
7. 必须生成至少8条不同角度的推文

请直接输出推文内容，不要输出其他解释。`

export default function Home() {
    const [files, setFiles] = useState([])  // 存储文件内容
    const [tweets, setTweets] = useState([])
    const [prompt, setPrompt] = useState(DEFAULT_PROMPT)
    const [loading, setLoading] = useState(false)
    const [toast, setToast] = useState(null)
    const [error, setError] = useState(null)
    const fileInputRef = useRef(null)

    const showToast = (message, type = 'info') => {
        setToast({ message, type })
        setTimeout(() => setToast(null), 3000)
    }

    const handleFiles = async (fileList) => {
        const newFiles = []

        for (const file of fileList) {
            if (!file.name.endsWith('.html')) continue

            const content = await file.text()
            newFiles.push({
                name: file.name,
                content,
                size: content.length
            })
        }

        setFiles(newFiles)
        setTweets([])
        setError(null)
        showToast(`已加载 ${newFiles.length} 个文件`, 'success')
    }

    const handleDrop = (e) => {
        e.preventDefault()
        handleFiles(e.dataTransfer.files)
    }

    const generateAllTweets = async () => {
        if (files.length === 0) {
            showToast('请先上传 HTML 文件', 'error')
            return
        }

        setLoading(true)
        setTweets([])
        setError(null)

        const allTweets = []

        for (const file of files) {
            try {
                showToast(`正在处理: ${file.name}`, 'info')

                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        htmlContent: file.content,
                        prompt
                    })
                })

                const data = await res.json()

                if (data.success && data.tweets) {
                    allTweets.push({
                        filename: file.name,
                        tweets: data.tweets
                    })
                } else {
                    setError(data.error || '生成失败')
                }
            } catch (err) {
                console.error('Generate error:', err)
                setError(err.message)
            }
        }

        setTweets(allTweets)
        setLoading(false)

        if (allTweets.length > 0) {
            const total = allTweets.reduce((sum, m) => sum + m.tweets.length, 0)
            showToast(`生成完成，共 ${total} 条推文`, 'success')
        }
    }

    const copyTweet = (text) => {
        navigator.clipboard.writeText(text)
        showToast('已复制', 'success')
    }

    const copyAll = () => {
        const allText = tweets.map(f =>
            `=== ${f.filename} ===\n\n${f.tweets.join('\n\n---\n\n')}`
        ).join('\n\n\n')
        navigator.clipboard.writeText(allText)
        showToast('已复制全部', 'success')
    }

    const exportJSON = () => {
        const blob = new Blob([JSON.stringify(tweets, null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'tweets.json'
        a.click()
    }

    const totalTweets = tweets.reduce((sum, f) => sum + f.tweets.length, 0)

    return (
        <div className="container">
            <header>
                <h1>🌸 Wiki → Twitter 动态生成器</h1>
                <p>上传 Fandom Wiki HTML，使用 AI 自动生成 Twitter 风格动态</p>
            </header>

            <div className="main-grid">
                {/* Left Panel - Upload & Prompt */}
                <div>
                    {/* Upload */}
                    <div className="panel">
                        <div className="panel-title">
                            <span>📁</span> 上传 HTML 文件
                        </div>
                        <div
                            className="upload-area"
                            onClick={() => fileInputRef.current?.click()}
                            onDragOver={(e) => e.preventDefault()}
                            onDrop={handleDrop}
                        >
                            <div className="icon">📄</div>
                            <p>拖拽文件到这里，或点击选择</p>
                            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>支持批量上传 .html 文件</p>
                        </div>
                        <input
                            ref={fileInputRef}
                            type="file"
                            multiple
                            accept=".html"
                            style={{ display: 'none' }}
                            onChange={(e) => handleFiles(e.target.files)}
                        />

                        {files.length > 0 && (
                            <div style={{ marginTop: 16 }}>
                                {files.map((f, i) => (
                                    <div key={i} style={{
                                        padding: '10px 14px',
                                        background: 'var(--bg)',
                                        borderRadius: 8,
                                        marginBottom: 8,
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center'
                                    }}>
                                        <span>📄 {f.name}</span>
                                        <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                                            {(f.size / 1024).toFixed(1)} KB
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Prompt */}
                    <div className="panel">
                        <div className="panel-title">
                            <span>✨</span> Prompt 设置
                        </div>
                        <div className="prompt-editor">
                            <textarea
                                value={prompt}
                                onChange={(e) => setPrompt(e.target.value)}
                                placeholder="编辑 Prompt..."
                            />
                        </div>
                        <div style={{ marginTop: 12, display: 'flex', gap: 10 }}>
                            <button className="btn btn-secondary btn-small" onClick={() => setPrompt(DEFAULT_PROMPT)}>
                                重置默认
                            </button>
                        </div>
                        <div style={{ marginTop: 20 }}>
                            <button
                                className="btn btn-primary"
                                onClick={generateAllTweets}
                                disabled={loading || files.length === 0}
                                style={{ width: '100%', justifyContent: 'center' }}
                            >
                                {loading ? '⏳ 生成中...' : `🚀 生成推文 (${files.length} 个文件)`}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right Panel - Results */}
                <div>
                    <div className="panel" style={{ minHeight: 500 }}>
                        <div className="panel-title">
                            <span>🐦</span> 生成结果
                            {totalTweets > 0 && (
                                <span style={{ marginLeft: 'auto', fontSize: 14, color: 'var(--text-secondary)' }}>
                                    共 {totalTweets} 条推文
                                </span>
                            )}
                        </div>

                        {error && (
                            <div style={{
                                padding: 16,
                                background: 'rgba(224, 36, 94, 0.1)',
                                border: '1px solid var(--error)',
                                borderRadius: 8,
                                marginBottom: 16,
                                color: 'var(--error)'
                            }}>
                                ❌ {error}
                            </div>
                        )}

                        {loading ? (
                            <div className="loading">
                                <div className="spinner"></div>
                            </div>
                        ) : tweets.length > 0 ? (
                            <div>
                                {tweets.map((file, fi) => (
                                    <div key={fi} style={{ marginBottom: 24 }}>
                                        <div style={{
                                            fontSize: 16,
                                            fontWeight: 700,
                                            marginBottom: 12,
                                            padding: '8px 12px',
                                            background: 'var(--bg)',
                                            borderRadius: 8,
                                            borderLeft: '3px solid var(--primary)'
                                        }}>
                                            📄 {file.filename}
                                            <span style={{ color: 'var(--text-secondary)', fontWeight: 400, marginLeft: 8 }}>
                                                ({file.tweets.length} 条)
                                            </span>
                                        </div>
                                        {file.tweets.map((tweet, ti) => (
                                            <div className="tweet-card" key={ti}>
                                                <div className="tweet-header">
                                                    <div className="tweet-number">{ti + 1}</div>
                                                    <div className="tweet-actions">
                                                        <button className="tweet-action" onClick={() => copyTweet(tweet)}>📋 复制</button>
                                                    </div>
                                                </div>
                                                <div className="tweet-content">{tweet}</div>
                                                <div className="tweet-meta">
                                                    <span className={`char-count ${tweet.length > 280 ? 'error' : tweet.length > 250 ? 'warning' : ''}`}>
                                                        {tweet.length}/280
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ))}

                                <div className="export-buttons">
                                    <button className="btn btn-secondary btn-small" onClick={copyAll}>📋 复制全部</button>
                                    <button className="btn btn-secondary btn-small" onClick={exportJSON}>💾 导出 JSON</button>
                                </div>
                            </div>
                        ) : (
                            <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 60 }}>
                                {files.length > 0
                                    ? '点击「生成推文」开始生成'
                                    : '上传 HTML 文件开始使用'}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {toast && (
                <div className={`toast ${toast.type}`}>
                    {toast.message}
                </div>
            )}
        </div>
    )
}
