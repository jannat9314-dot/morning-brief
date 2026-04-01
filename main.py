import requests
import os
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# -------- CONFIG --------
WEATHER_API = os.getenv("WEATHER_API")
NEWS_API = os.getenv("NEWS_API")
OPENAI_API = os.getenv("OPENAI_API")
EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

CITY = "Ludhiana"

# -------- DATE --------
today = datetime.now().strftime("%B %d, %Y")

# -------- WEATHER --------
weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API}&units=metric"

weather_res = requests.get(weather_url)
weather_data = weather_res.json()

if weather_data.get("cod") != 200:
    temp = "N/A"
    weather = "N/A"
else:
    temp = weather_data["main"]["temp"]
    weather = weather_data["weather"][0]["description"]

# -------- NEWS --------
news_url = f"https://gnews.io/api/v4/top-headlines?country=in&lang=en&token={NEWS_API}"
news_res = requests.get(news_url)
news_data = news_res.json()

articles = news_data.get("articles", [])[:8]

raw_news = ""
for article in articles:
    raw_news += f"""
Title: {article.get('title')}
Description: {article.get('description')}
Source: {article.get('source', {}).get('name')}
"""

# -------- AI --------
client = OpenAI(api_key=OPENAI_API)

prompt = f"""
Date: {today}

You are my daily morning briefing assistant.

About me:
Jannat Kondal, 1st year CSE student.
I care about: coding, AI, startups, geopolitics, Indian tech ecosystem.

Your job:
Give me a HIGH-SIGNAL morning briefing.

Rules:
- 5–7 important stories
- Focus: AI, tech, startups, geopolitics
- Skip noise

For EACH:
• Bold headline  
• 3–5 sentence summary  
• Why it matters to me  
• “So what” takeaway  

Tone:
Smart, sharp, no fluff.

Weather:
{temp}°C, {weather}

News:
{raw_news}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

ai_output = response.choices[0].message.content

# -------- EMAIL --------
msg = MIMEText(ai_output)
msg["Subject"] = f"Morning Briefing - {today} ☀️"
msg["From"] = EMAIL
msg["To"] = EMAIL

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(EMAIL, APP_PASSWORD)
    server.send_message(msg)

print("Email sent successfully ✅")
