import json
import os
import re

src_path = 'datas/local_config.json'

if not os.path.exists(src_path):
    print(f"❌ 核心错误：找不到下载的文件 {src_path}")
    exit(1)

# 宽松兼容的读取模式（兼容原作者可能遗留的 // 注释）
with open(src_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 剃掉可能导致解析失败的行注释和块注释
content = re.sub(r'//.*', '', content)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

try:
    data = json.loads(content)
except Exception:
    try:
        if '{' in content and '}' in content:
            content = content[content.find('{'):content.rfind('}')+1]
        data = eval(content, {"true": True, "false": False, "null": None})
    except Exception as e:
        print(f"❌ 文件解析彻底失败: {e}，请检查上游源是否正常。")
        exit(1)

# ==================== 核心逻辑：原封不动，直接输出 ====================
with open(src_path, 'w', encoding='utf-8') as f:
    # ensure_ascii=False 确保中文不变成 \uXXXX 这样的乱码字符
    # indent=2 保持标准的缩进排版，方便人类阅读
    json.dump(data, f, ensure_ascii=False, indent=2)

print("🎉 海豚源已原封不动、完整规范化同步盘存！")
