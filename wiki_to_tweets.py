#!/usr/bin/env python3
"""
Wiki to Twitter Posts Converter
将日向坂46 Fandom Wiki HTML页面转换为Twitter风格的动态
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import Optional, List
import subprocess


@dataclass
class MemberProfile:
    """成员资料数据类"""
    name_en: str
    name_jp: str = ""
    nickname: str = ""
    birthday: str = ""
    birthplace: str = ""
    blood_type: str = ""
    zodiac: str = ""
    height: str = ""
    occupation: str = ""
    years_active: str = ""
    agency: str = ""
    generation: str = ""
    group: str = ""
    bio: str = ""  # 简介/描述


def parse_wiki_html(html_path: str) -> MemberProfile:
    """解析Wiki HTML文件，提取成员资料"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # 获取英文名（从标题）
    title_elem = soup.find('h1', class_='page-header__title')
    name_en = ""
    if title_elem:
        span = title_elem.find('span', class_='mw-page-title-main')
        if span:
            name_en = span.get_text(strip=True)
        else:
            name_en = title_elem.get_text(strip=True)

    # 从infobox提取数据
    infobox = soup.find('aside', class_='portable-infobox')

    profile = MemberProfile(name_en=name_en)

    if not infobox:
        # 尝试从meta description获取基本信息
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            profile.bio = meta_desc.get('content', '')
        return profile

    # 获取日文名
    title_h2 = infobox.find('h2', class_='pi-title')
    if title_h2:
        ruby_tags = title_h2.find_all('ruby')
        if ruby_tags:
            jp_name_parts = []
            for ruby in ruby_tags:
                rb = ruby.find('rb')
                if rb:
                    jp_name_parts.append(rb.get_text(strip=True))
            profile.name_jp = ''.join(jp_name_parts)

    # 提取各项数据
    data_items = infobox.find_all('div', class_='pi-data')

    for item in data_items:
        label = item.find('h3', class_='pi-data-label')
        value = item.find('div', class_='pi-data-value')

        if not label or not value:
            continue

        label_text = label.get_text(strip=True).lower()
        value_text = value.get_text(strip=True)

        # 清理value_text中的多余内容
        value_text = re.sub(r'\s+', ' ', value_text)

        if 'nickname' in label_text:
            profile.nickname = value_text
        elif 'born' in label_text or 'birthday' in label_text:
            profile.birthday = value_text
        elif 'birthplace' in label_text:
            profile.birthplace = value_text
        elif 'blood' in label_text:
            profile.blood_type = value_text
        elif 'zodiac' in label_text:
            profile.zodiac = value_text
        elif 'height' in label_text:
            profile.height = value_text
        elif 'occupation' in label_text:
            profile.occupation = value_text
        elif 'years active' in label_text or 'active' in label_text:
            profile.years_active = value_text
        elif 'agency' in label_text:
            profile.agency = value_text
        elif 'generation' in label_text:
            profile.generation = value_text

    # 获取简介（从meta description或正文）
    meta_desc = soup.find('meta', {'name': 'description'})
    if meta_desc:
        profile.bio = meta_desc.get('content', '')

    # 判断所属团体
    if 'hinatazaka' in html_path.lower() or 'hinata' in str(infobox).lower():
        profile.group = "Hinatazaka46"
    elif 'nogizaka' in html_path.lower():
        profile.group = "Nogizaka46"
    elif 'sakurazaka' in html_path.lower():
        profile.group = "Sakurazaka46"

    return profile


def call_gemini_via_node(prompt: str) -> Optional[str]:
    """通过 Node.js ai-sdk 调用 Gemini API"""
    ai_script_dir = Path('/Users/jason/Downloads/workflow/llm-api/ai-script')

    if not ai_script_dir.exists():
        return None

    try:
        result = subprocess.run(
            ['node', 'index.js', prompt],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(ai_script_dir)
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            if result.stderr:
                print(f"Node.js 错误: {result.stderr[:200]}")
            return None

    except subprocess.TimeoutExpired:
        print("Gemini 调用超时")
        return None
    except FileNotFoundError:
        print("未找到 Node.js")
        return None
    except Exception as e:
        print(f"Gemini 调用失败: {e}")
        return None


def call_gemini_api(prompt: str, credential_path: str) -> Optional[str]:
    """调用 Google Vertex AI (Gemini) API - REST 方式"""
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        import requests

        # 读取凭证
        with open(credential_path, 'r') as f:
            creds_data = json.load(f)

        credentials = service_account.Credentials.from_service_account_file(
            credential_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

        # 获取访问令牌
        credentials.refresh(Request())
        access_token = credentials.token

        project_id = creds_data['project_id']
        location = 'asia-northeast1'

        # 尝试多个模型版本
        models_to_try = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro'
        ]

        for model in models_to_try:
            url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent"

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            data = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "maxOutputTokens": 1024,
                    "temperature": 0.8
                }
            }

            try:
                response = requests.post(url, headers=headers, json=data, timeout=60)
                if response.status_code == 200:
                    result = response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
            except:
                continue

        return None

    except ImportError as e:
        return None
    except Exception as e:
        print(f"Gemini REST API失败: {e}")
        return None


def generate_tweets_with_ai(profile: MemberProfile, api_key: Optional[str] = None) -> List[str]:
    """使用AI生成Twitter风格的动态"""

    profile_dict = asdict(profile)
    profile_json = json.dumps(profile_dict, ensure_ascii=False, indent=2)

    prompt = f"""你是一个专业的偶像粉丝账号运营者。根据以下日向坂46成员的资料，生成8-10条Twitter风格的动态（推文）。

成员资料：
{profile_json}

要求：
1. 每条推文不超过280字符（中文约140字）
2. 可以包含emoji，但不要过多
3. 风格要像真实的粉丝分享，有热情但不夸张
4. 推文类型要多样化，包括但不限于：
   - 成员基本介绍
   - 生日祝福模板（只在生日当天生成）
   - 昵称/外号趣事
   - 身高/星座/血型等冷知识
   - 出身地相关
   - 加入团体的经历
   - 鼓励应援的内容
   - 日常安利推荐
   - 和其他成员的关系
   - 绝技、绝招
   - 爱好
   - 如果有动物塑，可以发挥一下
   - 如果有应援色，可以说明
5. 使用日文撰写
6. 每条推文用 "---" 分隔
7. 必须生成至少8条不同角度的推文
8. 不要加hashtag

请直接输出推文内容，不要输出其他解释。"""

    # 优先使用 Node.js ai-sdk 调用 Gemini（最可靠）
    ai_script_dir = Path('/Users/jason/Downloads/workflow/llm-api/ai-script')
    if ai_script_dir.exists():
        print("  使用 Gemini API (Node.js)")
        response_text = call_gemini_via_node(prompt)
        if response_text:
            tweets = [t.strip() for t in response_text.split('---') if t.strip()]
            if tweets:
                return tweets

    # 备选：使用 REST API 调用 Gemini
    credential_paths = [
        Path(__file__).parent / 'credential.json',
        Path('/Users/jason/Downloads/workflow/llm-api/ai-script/credential.json'),
        Path.home() / '.config' / 'gcloud' / 'application_default_credentials.json'
    ]

    for cred_path in credential_paths:
        if cred_path.exists():
            print(f"  使用 Gemini REST API ({cred_path.name})")
            response_text = call_gemini_api(prompt, str(cred_path))
            if response_text:
                tweets = [t.strip() for t in response_text.split('---') if t.strip()]
                if tweets:
                    return tweets
            break

    # 尝试使用Claude API（通过环境变量）
    if api_key or os.environ.get('ANTHROPIC_API_KEY'):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

            print("  使用 Claude API")
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            tweets = [t.strip() for t in response_text.split('---') if t.strip()]
            return tweets
        except ImportError:
            pass
        except Exception as e:
            print(f"Claude API调用失败: {e}")

    # 尝试使用OpenAI API
    if os.environ.get('OPENAI_API_KEY'):
        try:
            import openai
            client = openai.OpenAI()

            print("  使用 OpenAI API")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024
            )

            response_text = response.choices[0].message.content
            tweets = [t.strip() for t in response_text.split('---') if t.strip()]
            return tweets
        except ImportError:
            pass
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")

    # 尝试使用本地 Ollama
    try:
        print("  使用 Ollama")
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2', prompt],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            response_text = result.stdout
            tweets = [t.strip() for t in response_text.split('---') if t.strip()]
            if tweets:
                return tweets
    except FileNotFoundError:
        pass
    except subprocess.TimeoutExpired:
        print("Ollama 超时")
    except Exception as e:
        print(f"Ollama调用失败: {e}")

    # 回退：使用模板生成基础推文
    print("  使用模板模式")
    return generate_template_tweets(profile)


def generate_template_tweets(profile: MemberProfile) -> List[str]:
    """使用模板生成基础推文（无AI时的回退方案）"""
    tweets = []

    name = profile.name_jp if profile.name_jp else profile.name_en

    # 介绍推文
    intro = f"【成员介绍】{name}"
    if profile.group:
        intro += f" 是 {profile.group} 的成员"
    if profile.generation:
        intro += f"（{profile.generation}）"
    intro += " ✨"
    tweets.append(intro)

    # 基本信息
    if profile.birthday:
        tweets.append(f"🎂 {name} 的生日是 {profile.birthday}！记得为她庆祝哦～")

    if profile.birthplace:
        tweets.append(f"📍 {name} 来自{profile.birthplace}，是不是很想去她的家乡看看呢？")

    if profile.nickname:
        tweets.append(f"💫 你知道吗？{name} 的昵称是「{profile.nickname}」，很可爱吧！")

    if profile.height:
        tweets.append(f"📏 {name} 身高 {profile.height}，在舞台上真的很耀眼！")

    if profile.zodiac and profile.blood_type:
        tweets.append(f"⭐ {name} 是{profile.zodiac}座，血型{profile.blood_type}型～你和她匹配吗？")

    return tweets[:5]  # 最多返回5条


def process_wiki_folder(wiki_folder: str, output_file: str = "tweets_output.json"):
    """处理整个Wiki文件夹，生成推文"""

    wiki_path = Path(wiki_folder)
    html_files = list(wiki_path.rglob("*.html"))

    if not html_files:
        print(f"未找到HTML文件: {wiki_folder}")
        return

    print(f"找到 {len(html_files)} 个HTML文件")

    all_results = []
    tweet_id = 1

    for html_file in html_files:
        print(f"\n处理: {html_file.name}")

        try:
            profile = parse_wiki_html(str(html_file))

            if not profile.name_en:
                print(f"  跳过（无法提取名字）")
                continue

            print(f"  成员: {profile.name_en} ({profile.name_jp})")

            tweets = generate_tweets_with_ai(profile)

            # 使用扁平格式：每条推文一个对象
            for tweet in tweets:
                all_results.append({
                    "id": tweet_id,
                    "ip": profile.group or "Hinatazaka46",
                    "content": tweet
                })
                tweet_id += 1

            print(f"  生成了 {len(tweets)} 条推文")

        except Exception as e:
            print(f"  错误: {e}")

    # 保存结果
    output_path = Path(wiki_folder) / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n完成！结果已保存到: {output_path}")
    print(f"共处理 {len(all_results)} 个成员")

    return all_results


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='将Fandom Wiki HTML转换为Twitter动态',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python wiki_to_tweets.py                    # 处理当前目录
  python wiki_to_tweets.py ./info             # 处理指定目录
  python wiki_to_tweets.py -o my_tweets.json  # 指定输出文件

环境变量:
  ANTHROPIC_API_KEY  - Claude API密钥（推荐）
  OPENAI_API_KEY     - OpenAI API密钥

如果没有设置API密钥，将尝试使用本地Ollama，或回退到模板生成。
        """
    )

    parser.add_argument(
        'wiki_folder',
        nargs='?',
        default='.',
        help='Wiki HTML文件所在目录 (默认: 当前目录)'
    )

    parser.add_argument(
        '-o', '--output',
        default='tweets_output.json',
        help='输出文件名 (默认: tweets_output.json)'
    )

    parser.add_argument(
        '--single',
        help='只处理单个HTML文件'
    )

    parser.add_argument(
        '--preview',
        action='store_true',
        help='预览模式：只解析不生成推文'
    )

    args = parser.parse_args()

    if args.single:
        # 处理单个文件
        print(f"处理单个文件: {args.single}")
        profile = parse_wiki_html(args.single)
        print("\n=== 提取的资料 ===")
        for key, value in asdict(profile).items():
            if value:
                print(f"  {key}: {value}")

        if not args.preview:
            print("\n=== 生成的推文 ===")
            tweets = generate_tweets_with_ai(profile)
            for i, tweet in enumerate(tweets, 1):
                print(f"\n[{i}] {tweet}")
    else:
        # 处理整个目录
        if args.preview:
            # 预览模式
            wiki_path = Path(args.wiki_folder)
            html_files = list(wiki_path.rglob("*.html"))
            print(f"找到 {len(html_files)} 个HTML文件:\n")

            for html_file in html_files[:5]:  # 只预览前5个
                profile = parse_wiki_html(str(html_file))
                print(f"📄 {html_file.name}")
                print(f"   成员: {profile.name_en} ({profile.name_jp})")
                if profile.birthday:
                    print(f"   生日: {profile.birthday}")
                print()

            if len(html_files) > 5:
                print(f"... 还有 {len(html_files) - 5} 个文件")
        else:
            process_wiki_folder(args.wiki_folder, args.output)


if __name__ == '__main__':
    main()
