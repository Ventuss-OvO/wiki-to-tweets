# Wiki to Twitter 动态生成器

将日向坂46 Fandom Wiki HTML页面转换为Twitter风格的动态。

## 快速开始

```bash
# 简易交互模式
python3 run.py

# 或者直接使用命令行
python3 wiki_to_tweets.py --preview          # 预览模式
python3 wiki_to_tweets.py ./info             # 处理info目录
python3 wiki_to_tweets.py --single "xxx.html" # 处理单个文件
```

## AI 配置

脚本支持多种AI后端，按优先级：

1. **Google Gemini** (默认，通过 Node.js ai-sdk)
   - 使用 `/Users/jason/Downloads/workflow/llm-api/ai-script/` 的配置
   - 自动读取 credential.json

2. **Claude API**
   ```bash
   export ANTHROPIC_API_KEY="your-key"
   ```

3. **OpenAI API**
   ```bash
   export OPENAI_API_KEY="your-key"
   ```

4. **本地 Ollama**
   - 安装 [Ollama](https://ollama.ai)
   - 运行 `ollama pull llama3.2`

5. **模板模式** (无需AI)
   - 如果没有配置任何AI，会使用内置模板生成基础推文

## 输出

处理完成后，结果保存在 `tweets_output.json`，格式如下：

```json
[
  {
    "source_file": "xxx.html",
    "member_name": "Kanemura Miku",
    "member_name_jp": "金村美玖",
    "profile": { ... },
    "tweets": [
      "推文1",
      "推文2"
    ]
  }
]
```

## 示例输出

```
[1] 阳光活力的日向坂46二期生金村美玖！不仅是舞台上闪耀的偶像，更是时尚杂志的常驻模特✨
    她的笑容真的太治愈了，不愧是我们的"寿司"お寿司🍣 #金村美玖 #日向坂46

[2] 提前Mark住！日向坂46的颜值担当金村美玖的生日是9月10日！
    期待那天美玖会带来什么惊喜呢？大家一起准备好祝福吧🎂 #金村美玖生誕祭
```

## 依赖

- Python 3.7+
- beautifulsoup4
- Node.js (用于 Gemini API)
