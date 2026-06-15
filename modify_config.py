import json
import os

# 定义多源文件路径
src_cnb_path = 'datas/source1.json'   # 上游A：CNB 仓库
src_gh_path = 'datas/source2.json'    # 上游B：海豚源
output_path = 'datas/local_config.json'

# 初始化一个完全属于你自己的全新、干净的本地框架
final_data = {
    "spider": "./tvbox.jar",
    "logo": "https://your-domain.com/my-logo.png",
    "wallpaper": "http://tool.teyonds.com/api",
    "warningText": "欢迎使用老杨专线，完全免费，如果收费都是骗子！",
    "sites": [],
    "parses": [],
    "lives": []
}

# 辅助函数：安全读取 JSON 文件
def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"警告：{path} 格式有误，解析失败，跳过。")
    return {}

data_cnb = load_json(src_cnb_path)
data_gh = load_json(src_gh_path)

# 动态继承一下上游的 spider 核心（优先用 CNB 的）
if 'spider' in data_cnb: final_data['spider'] = data_cnb['spider']
elif 'spider' in data_gh: final_data['spider'] = data_gh['spider']

# 全局四大厂黑名单
black_list = ["爱奇艺", "优酷", "腾讯", "芒果"]

# 用于全局去重的集合
seen_site_keys = set()
seen_live_urls = set()
seen_parse_urls = set()

# ==================== 1. 精准清洗并提取 CNB 仓库 (上游A) ====================
if 'sites' in data_cnb and isinstance(data_cnb['sites'], list):
    for site in data_cnb['sites']:
        key = site.get('key')
        name = site.get('name', '')
        
        # 规则1：全局过滤四大厂
        if any(k in name for k in black_list):
            continue
            
        # 规则2：CNB 仓库里非 APP 线路全部去掉（必须带有“APP”或“丨APP”字样才保留）
        # 这里统一检测名字里是否包含 "APP" 或 "App"
        if "APP" not in name.upper():
            continue
            
        # 去重验证并加入最终列表
        if key not in seen_site_keys:
            seen_site_keys.add(key)
            final_data['sites'].append(site)

# 规则3：CNB 仓库里的直播源（lives）全部去掉 -> 所以这里直接【不处理】data_cnb 的 lives

# ==================== 2. 清洗、提取并合流海豚仓库 (上游B) ====================
# 2.1 处理海豚源的视频站 (sites)
if 'sites' in data_gh and isinstance(data_gh['sites'], list):
    for site in data_gh['sites']:
        key = site.get('key')
        name = site.get('name', '')
        
        # 规则1：全局过滤四大厂
        if any(k in name for k in black_list):
            continue
            
        # 去重：如果这个站的 key 在刚才 CNB 提取的 APP 线路里已经存在了，直接跳过
        if key in seen_site_keys:
            continue
            
        seen_site_keys.add(key)
        final_data['sites'].append(site) # 缝合进来

# 2.2 处理海豚源的直播源 (lives) - 只保留海豚源的直播
if 'lives' in data_gh and isinstance(data_gh['lives'], list):
    for live in data_gh['lives']:
        url = live.get('url')
        name = live.get('name', '')
        
        # 同样过滤掉直播名里包含四大厂的（虽然直播里很少见，但安全第一）
        if any(k in name for k in black_list):
            continue
            
        if url not in seen_live_urls:
            seen_live_urls.add(url)
            final_data['lives'].append(live)

# ==================== 3. 提取并合并双方的解析接口 (parses) ====================
all_parses = []
if 'parses' in data_cnb and isinstance(data_cnb['parses'], list): all_parses.extend(data_cnb['parses'])
if 'parses' in data_gh and isinstance(data_gh['parses'], list): all_parses.extend(data_gh['parses'])

for parse in all_parses:
    url = parse.get('url')
    if url and url not in seen_parse_urls:
        seen_parse_urls.add(url)
        final_data['parses'].append(parse)

# ==================== 4. 将干干净净的最终结果写入本地文件 ====================
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print("🎉 属于老杨自己的本地专属配置融合成功！")
print(f"最终视频站数：{len(final_data['sites'])}，最终直播源数：{len(final_data['lives'])}")
