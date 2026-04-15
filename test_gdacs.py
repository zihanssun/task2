import requests
import json 

# GDACS API 地址 — 完全公开，无需任何 Key！
url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"

# 查询参数：2025年8月的热带气旋
params = {
    "eventlist": "TC",                        # TC = Tropical Cyclone
    "fromDate": "2025-08-01",
    "toDate": "2025-08-31",
    "alertlevel": "Green;Orange;Red",         # 所有警报级别
}

# 发送请求
response = requests.get(url, params=params)

# 检查是否成功
if response.status_code == 200:
    data = response.json() #把文字变成dict
    events = data.get("features", [])
    print(f"🌀 找到 {len(events)} 个热带气旋事件（2025年8月）\n")
    
    for i, event in enumerate(events, 1):
        props = event["properties"]
        print(f"--- 事件 {i}: {props['eventname']} ---")
        print(f"  名称: {props['name']}")
        print(f"  时间: {props['fromdate']} ~ {props['todate']}")
        print(f"  影响国家: {props.get('country', '无 (海上)')}")
        print(f"  警报级别: {props['alertlevel']}")
        severity = props.get("severitydata", {})
        print(f"  最大风速: {severity.get('severitytext', 'N/A')}")
        coords = event["geometry"]["coordinates"]
        print(f"  坐标: 经度 {coords[0]}, 纬度 {coords[1]}")
        print()
else:
    print(f"❌ 请求失败，状态码: {response.status_code}")