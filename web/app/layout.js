import './globals.css'

export const metadata = {
    title: 'Wiki → Twitter 动态生成器',
    description: '将日向坂46 Fandom Wiki HTML 转换为 Twitter 风格动态',
    icons: {
        icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🧶</text></svg>',
    },
}

export default function RootLayout({ children }) {
    return (
        <html lang="zh-CN" suppressHydrationWarning>
            <body suppressHydrationWarning>{children}</body>
        </html>
    )
}
