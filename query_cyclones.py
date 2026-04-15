import requests
import json

def get_tropical_cyclones(from_date: str, to_date: str) -> list:
    """
    从 GDACS 获取指定时间范围内的热带气旋事件
    
    Args:
        from_date: 开始日期，格式"YYYY-MM-DD"
        to_date: 结束日期，格式"YYYY-MM-DD"
    
    Returns:
        事件列表，每个事件是一个字典
    """
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
    params = {
        "eventlist": "TC",
        "fromDate": from_date,
        "toDate": to_date,
        "alertlevel": "Green;Orange;Red",
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # 如果出错会抛出异常
    
    data = response.json()
    events = []
    
    for feature in data.get("features", []):
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]
        severity = props.get("severitydata", {})
        
        events.append({
            "name": props["eventname"],
            "full_name": props["name"],
            "from_date": props["fromdate"],
            "to_date": props["todate"],
            "country": props.get("country", "海上"),
            "alert_level": props["alertlevel"],
            "max_wind_speed_kmh": severity.get("severity"),
            "severity_text": severity.get("severitytext"),
            "longitude": coords[0],
            "latitude": coords[1],
            "source": props.get("source", "unknown"),
            "report_url": props.get("url", {}).get("report", ""),
        })
    
    return events


# 查询 2025 年 8 月
events = get_tropical_cyclones("2025-08-01", "2025-08-31")

print(f"\n🌀 2025年8月共有 {len(events)} 个热带气旋事件\n")

# 按警报级别分类
for level in ["Red", "Orange", "Green"]:
    level_events = [e for e in events if e["alert_level"] == level]
    if level_events:
        print(f"\n{'=' * 50}")
        print(f"警报级别: {level} ({len(level_events)} 个)")
        print(f"{'=' * 50}")
        for e in level_events:
            print(f"  • {e['name']}: {e['country']}")
            print(f"    {e['from_date'][:10]} ~ {e['to_date'][:10]}")
            print(f"    最大风速: {e['max_wind_speed_kmh']:.0f} km/h")

# 保存到 JSON
with open("cyclones_aug_2025.json", "w", encoding="utf-8") as f: 
    #with ... as f: 打开文件夹自动关闭，w：write，encoding：保持中文不乱码
    json.dump(events, f, ensure_ascii=False, indent=2)
    #ensure——ascii：保持中文不乱码，indent：缩进
print(f"\n💾 结果已保存到 cyclones_aug_2025.json")