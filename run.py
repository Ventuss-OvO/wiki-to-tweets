#!/usr/bin/env python3
"""
简易启动脚本 - Wiki转Twitter动态生成器
"""

import os
import sys
from pathlib import Path

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║          🌸 Wiki → Twitter 动态生成器 🌸                  ║
║              日向坂46 Fandom Wiki 转换工具                 ║
╚════════════════════════════════════════════════════════════╝

AI后端: Gemini (Google Vertex AI)
    """)

    # 检查依赖
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("正在安装依赖 beautifulsoup4...")
        os.system(f"{sys.executable} -m pip install beautifulsoup4 -q")
        from bs4 import BeautifulSoup

    # 导入主模块
    from wiki_to_tweets import process_wiki_folder, parse_wiki_html, generate_tweets_with_ai, asdict

    wiki_folder = Path(__file__).parent / "info"

    if not wiki_folder.exists():
        wiki_folder = Path(__file__).parent
        html_files = list(wiki_folder.rglob("*.html"))
        if not html_files:
            print("❌ 未找到HTML文件，请确保wiki文件夹中包含.html文件")
            return

    html_files = list(wiki_folder.rglob("*.html"))
    print(f"📁 找到 {len(html_files)} 个HTML文件\n")

    print("请选择操作模式：")
    print("  [1] 处理所有文件并生成推文")
    print("  [2] 只预览解析结果（不生成推文）")
    print("  [3] 处理单个成员")
    print("  [4] 退出")

    choice = input("\n请输入选项 (1-4): ").strip()

    if choice == '1':
        print("\n🚀 开始处理所有文件...\n")
        results = process_wiki_folder(str(wiki_folder))

        if results:
            print("\n" + "="*50)
            print("📝 部分生成结果预览：")
            print("="*50)

            for result in results[:3]:
                print(f"\n👤 {result['member_name']} ({result['member_name_jp']})")
                for i, tweet in enumerate(result['tweets'][:2], 1):
                    print(f"   [{i}] {tweet[:80]}..." if len(tweet) > 80 else f"   [{i}] {tweet}")

    elif choice == '2':
        print("\n📋 预览模式：\n")
        for html_file in html_files[:10]:
            profile = parse_wiki_html(str(html_file))
            if profile.name_en and profile.name_en != 'Hinatazaka46':
                print(f"✅ {profile.name_en} ({profile.name_jp})")
                if profile.birthday:
                    print(f"   🎂 {profile.birthday}")
                if profile.nickname:
                    print(f"   💫 {profile.nickname}")
                print()

        if len(html_files) > 10:
            print(f"... 还有 {len(html_files) - 10} 个文件")

    elif choice == '3':
        # 列出所有成员
        members = []
        for html_file in html_files:
            profile = parse_wiki_html(str(html_file))
            if profile.name_en and profile.name_en != 'Hinatazaka46':
                members.append((profile.name_en, profile.name_jp, str(html_file)))

        print("\n可用成员：")
        for i, (name_en, name_jp, _) in enumerate(members, 1):
            print(f"  [{i}] {name_en} ({name_jp})")

        try:
            idx = int(input("\n请输入成员编号: ")) - 1
            if 0 <= idx < len(members):
                name_en, name_jp, file_path = members[idx]
                print(f"\n处理: {name_en}")

                profile = parse_wiki_html(file_path)

                print("\n📋 资料：")
                for key, value in asdict(profile).items():
                    if value and key != 'bio':
                        print(f"   {key}: {value}")

                print("\n🐦 生成推文中...\n")
                tweets = generate_tweets_with_ai(profile)

                print("生成的推文：")
                for i, tweet in enumerate(tweets, 1):
                    print(f"\n[{i}] {tweet}")
            else:
                print("无效的编号")
        except ValueError:
            print("请输入有效的数字")

    elif choice == '4':
        print("再见！👋")
    else:
        print("无效的选项")


if __name__ == '__main__':
    main()
