import os
import requests
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

def query_gdacs_disasters(
    disaster_type: str,
    from_date: str,
    to_date: str
) -> str:
    """
    Query disaster events from the UN GDACS (Global Disaster Alert and Coordination System).
    This is a public API — no API key needed.
    
    Args:
        disaster_type: Type code — "TC" (Tropical Cyclone), "EQ" (Earthquake),
                       "FL" (Flood), "VO" (Volcano), "DR" (Drought), "WF" (Wildfire)
        from_date: Start date in YYYY-MM-DD format, e.g. "2025-08-01"
        to_date: End date in YYYY-MM-DD format, e.g. "2025-08-31"
    
    Returns:
        A summary of matching disaster events with names, dates, severity, and affected countries.
    """
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH"
    params = {
        "eventlist": disaster_type,
        "fromDate": from_date,
        "toDate": to_date,
        "alertlevel": "Green;Orange;Red",
    }
    
    try: #尝试运行一段代码 → 如果中途报错了，不崩溃，而是跳到 except 去处理错误。
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        features = data.get("features", [])
        
        if not features:
            return f"没有找到 {from_date} 到 {to_date} 期间的 {disaster_type} 事件。"
        
        # 构建摘要
        type_names = {
            "TC": "热带气旋", "EQ": "地震", "FL": "洪水",
            "VO": "火山", "DR": "干旱", "WF": "野火"
        }
        type_name = type_names.get(disaster_type, disaster_type)
        
        summary = f"找到 {len(features)} 个{type_name}事件（{from_date} ~ {to_date}): \n\n"
        
        for i, feature in enumerate(features, 1):
            props = feature["properties"]
            severity = props.get("severitydata", {})
            summary += f"{i}. **{props['eventname']}**\n"
            summary += f"   时间: {props['fromdate'][:10]} ~ {props['todate'][:10]}\n"
            summary += f"   影响地区: {props.get('country', '海上')}\n"
            summary += f"   警报级别: {props['alertlevel']}\n"
            if severity.get("severity"):
                summary += f"   最大风速: {severity['severity']:.0f} km/h\n"
            summary += "\n"
        
        return summary
        
    except Exception as e:
        return f"查询出错: {str(e)}"


# 创建 DeepSeek 模型
model = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
)

# 创建 Agent
agent = create_agent(
    model=model,
    tools=[query_gdacs_disasters],
    system_prompt="""你是一个灾害数据分析助手。你可以查询联合国 GDACS 全球灾害数据库。
    
    支持的灾害类型：
    - TC: 热带气旋（台风/飓风）
    - EQ: 地震
    - FL: 洪水
    - VO: 火山爆发
    - DR: 干旱
    - WF: 野火
    
    请用中文回答，并提供清晰的数据摘要。
    当用户提到"台风""飓风"时，使用 TC 类型查询。""",
)

# 测试 1：查询热带气旋
print("\n" + "="*50)
print("🌀 测试 1: 查询热带气旋")
print("="*50)
result = agent.invoke(
    {"messages": [{
        "role": "user",
        "content": "2025年8月有哪些热带气旋？哪些是最严重的？"
    }]}
)
print(result["messages"][-1].content)

# 测试 2：Agent 可以查询不同类型的灾害
print("\n" + "="*50)
print("🌋 测试 2: 查询其他灾害类型")
print("="*50)
result2 = agent.invoke(
    {"messages": [{
        "role": "user",
        "content": "2025年8月有没有发生过火山爆发？"
    }]}
)
print(result2["messages"][-1].content)