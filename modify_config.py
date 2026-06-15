import json
import os
import re

# 定义多源文件路径
src_cnb_path = 'datas/source1.json'   # 上游A：CNB 仓库
src_gh_path = 'datas/source2.json'    # 上游B：海豚源
output_path = 'datas/local_config.json'

# 初始化最终的基础配置框架
final_data = {
    "spider": "./tvbox.jar", 
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

# 终极宽松兼容 JSON 加载器（能强行掰正各类不规范影视 JSON 文本）
def load_json_permissive(path):
    if not os.path.exists(path):
        print(f"❌ 错误：找不到文件 {path}")
        return {}
        
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. 强行剃掉行尾带有 // 的影视接口注释
        content = re.sub(r'//.*', '', content)
        # 2. 强行剃掉块注释 /* ... */
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # 3. 尝试用标准 json 库解析
        return json.loads(content)
    except Exception:
        # 4. 如果标准库失败，使用 eval 进行宽限解包（兼容行尾多出逗号等不合规格式）
        try:
            # 提取可能存在的纯 JSON 括号段落
            if '{' in content and '}' in content:
                content = content[content.find('{'):content.rfind('}')+1]
            return eval(content, {"true": True, "false": False, "null": None})
        except Exception as e2:
            print(f"❌ 终极硬解文件 {path} 失败: {e2}")
            return {}

print("开始精准读取上游线路...")
data_cnb = load_json_permissive(src_cnb_path)
data_gh = load_json_permissive(src_gh_path)

# ==================== 0. 强行拉回核心的底层配置架构 ====================
# 优先从 CNB 中抓取 rules, flags, ads, doh 进 final_data，确保播放环境健全
for k in ["rules", "flags", "ads", "doh", "ijk"]:
    if data_cnb and k in data_cnb and data_cnb[k]:
        final_data[k] = data_cnb[k]
    elif data_gh and k in data_gh and data_gh[k]:
        final_data[k] = data_gh[k]

# 全局四大厂黑名单
black_list = ["爱奇艺", "优酷", "腾讯", "芒果"]

# 全局去重字典集合
seen_site_keys = set()
seen_live_urls = set()
seen_parse_urls = set()

# ==================== 1. 精准提取 CNB 仓库 (只留以 csp_App 开头的核心站) ====================
cnb_count = 0
if data_cnb and 'sites' in data_cnb and isinstance(data_cnb['sites'], list):
    for site in data_cnb['sites']:
        key = site.get('key', '')
        name = site.get('name', '')
        api = site.get('api', '')
        
        # 过滤四大大厂
        if any(k in name for k in black_list):
            continue
            
        # 【最精准规则】：CNB 仓库中，凡是核心 APP 站，其 api 字段必以 "csp_App" 开头！
        # 这样不仅能完美留存全部 APP 站，同时也能利落剔除豆瓣、Nostr、各种4K网盘和短剧线
        if not str(api).startswith("csp_App"):
            continue
            
        if key not in seen_site_keys:
            seen_site_keys.add(key)
            final_data['sites'].append(site)
            cnb_count += 1
    print(f"▶ CNB 仓库：成功加载并置顶了 {cnb_count} 个高端 APP 线路")
else:
    print("❌ 核心警告：CNB 文件未被成功读取或缺少 sites 数据！")

# ==================== 2. 清洗合并海豚仓库 (补足普通视频站点与全部直播) ====================
gh_count = 0
if data_gh and 'sites' in data_gh and isinstance(data_gh['sites'], list):
    for site in data_gh['sites']:
        key = site.get('key')
        name = site.get('name', '')
        
        if any(k in name for k in black_list):
            continue
        if key in seen_site_keys:
            continue
            
        seen_site_keys.add(key)
        final_data['sites'].append(site)
        gh_count += 1
    print(f"▶ 海豚仓库：成功互补吸纳了 {gh_count} 个普通视频站")

# 2.2 读取且仅读取海豚源的直播数据 (lives)
if data_gh and 'lives' in data_gh and isinstance(data_gh['lives'], list):
    for live in data_gh['lives']:
        url = live.get('url')
        name = live.get('name', '')
        
        if any(k in name for k in black_list):
            continue
        if url not in seen_live_urls:
            seen_live_urls.add(url)
            final_data['lives'].append(live)
    print(f"▶ 直播合流：成功洗出 {len(final_data['lives'])} 条无广告直播源")

# ==================== 3. 提取并清洗双方的解析接口 (parses) ====================
all_parses = []
if data_cnb and 'parses' in data_cnb and isinstance(data_cnb['parses'], list): 
    all_parses.extend(data_cnb['parses'])
if data_gh and 'parses' in data_gh and isinstance(data_gh['parses'], list): 
    all_parses.extend(data_gh['parses'])

for parse in all_parses:
    url = parse.get('url')
    if url and url not in seen_parse_urls:
        seen_parse_urls.add(url)
        final_data['parses'].append(parse)

# ==================== 4. 强制复写，重新导出本地文件 ====================
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print("🎉 终极洗牌结束，数据已完全规整导出。")
