import './globals.css'

export const metadata = {
    title: 'Wiki → Twitter 动态生成器',
    description: '将日向坂46 Fandom Wiki HTML 转换为 Twitter 风格动态',
}

export default function RootLayout({ children }) {
    return (
        <html lang="zh-CN">
            <body>{children}</body>
        </html>
    )
}
