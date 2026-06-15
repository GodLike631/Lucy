import json
import os
import re

# 定义多源文件路径
src_cnb_path = 'datas/source1.json'   # 上游A：CNB 仓库
src_gh_path = 'datas/source2.json'    # 上游B：海豚源
output_path = 'datas/local_config.json'

# 构建完全属于你的、带有完整底层规则的基础大框架
final_data = {
    "spider": "./tvbox.jar",  # 强制锁死为最通用的 tvbox 核心，防止被 cnb 的配置带偏
    "logo": "https://your-domain.com/my-logo.png",
    "wallpaper": "http://tool.teyonds.com/api",
    "warningText": "欢迎使用老杨专线，完全免费，如果收费都是骗子！",
    "sites": [],
    "parses": [],
    "lives": [],
    "rules": [],
    "flags": [],
    "ads": [],
    "doh": []
}

# 升级版辅助函数：强行修复标准 JSON 格式并读取
def load_json_permissive(path):
    if not os.path.exists(path):
        print(f"❌ 错误：找不到文件 {path}")
        return {}
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 强行用正则切除影视接口中常见的 // 注释
    content = re.sub(r'//.*', '', content)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            # 兼容非标准标准尾部逗号的情况
            return eval(content, {"true": True, "false": False, "null": None})
        except Exception:
            return {}

print("开始精准读取上游线路...")
data_cnb = load_json_permissive(src_cnb_path)
data_gh = load_json_permissive(src_gh_path)

# ==================== 0. 继承 CNB 仓库的高级底层规则 ====================
# 这些规则决定了 4K 资源和内置线路能否播得出来，必须继承
for key in ["rules", "flags", "ads", "doh", "ijk"]:
    if key in data_cnb:
        final_data[key] = data_cnb[key]
    elif key in data_gh and key not in final_data:
        final_data[key] = data_gh[key]

# 全局四大厂黑名单
black_list = ["爱奇艺", "优酷", "腾讯", "芒果"]

# 全局去重集合
seen_site_keys = set()
seen_live_urls = set()
seen_parse_urls = set()

# ==================== 1. 精准清洗并提取 CNB 仓库的 APP 线路 ====================
cnb_count = 0
if 'sites' in data_cnb and isinstance(data_cnb['sites'], list):
    for site in data_cnb['sites']:
        key = site.get('key', '')
        name = site.get('name', '')
        
        # 1. 过滤四大厂
        if any(k in name for k in black_list):
            continue
            
        # 2. CNB 仓库定向清洗：名字中必须包含 APP / App 或者是你指定的那些特定大厂应用源
        # 考虑到全角半角符号（｜/ 丨），我们直接用 upper 匹配纯字母
        is_app_line = "APP" in name.upper() or "APP" in str(key).upper()
        
        if not is_app_line:
            continue  # 不是 APP 线路，无情剔除（如豆瓣、Nostr、玩偶等非APP线）
            
        if key not in seen_site_keys:
            seen_site_keys.add(key)
            final_data['sites'].append(site)
            cnb_count += 1
    print(f"▶ CNB 仓库：成功提取并锁定了 {cnb_count} 个核心 APP 线路")

# ==================== 2. 清洗、提取并合流海豚仓库 ====================
gh_count = 0
if 'sites' in data_gh and isinstance(data_gh['sites'], list):
    for site in data_gh['sites']:
        key = site.get('key')
        name = site.get('name', '')
        
        if any(k in name for k in black_list):
            continue
        if key in seen_site_keys:
            continue # 如果 CNB 里已经有了，保留 CNB 的最新版
            
        seen_site_keys.add(key)
        final_data['sites'].append(site)
        gh_count += 1
    print(f"▶ 海豚仓库：成功合流了 {gh_count} 个互补普通线路")

# 2.2 处理海豚源的直播源 (lives) - 彻底抛弃 CNB 的，只留海豚的
if 'lives' in data_gh and isinstance(data_gh['lives'], list):
    for live in data_gh['lives']:
        url = live.get('url')
        name = live.get('name', '')
        if any(k in name for k in black_list): 
            continue
        if url not in seen_live_urls:
            seen_live_urls.add(url)
            final_data['lives'].append(live)
    print(f"▶ 直播合流：成功载入 {len(final_data['lives'])} 条无广告直播线路")

# ==================== 3. 提取并合并双方的解析接口 (parses) ====================
all_parses = []
if 'parses' in data_cnb and isinstance(data_cnb['parses'], list): all_parses.extend(data_cnb['parses'])
if 'parses' in data_gh and isinstance(data_gh['parses'], list): all_parses.extend(data_gh['parses'])

for parse in all_parses:
    url = parse.get('url')
    if url and url not in seen_parse_urls:
        seen_parse_urls.add(url)
        final_data['parses'].append(parse)

# ==================== 4. 将提纯后的完美大文件写入本地 ====================
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print("🎉 终极多源沙箱清洗缝合成功，格式完美兼容！")
