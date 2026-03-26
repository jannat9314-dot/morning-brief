import requests
import os
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
# -------- CONFIG --------
WEATHER_API = os.getenv("WEATHER_API")
NEWS_API = os.getenv("NEWS_API")
OPENAI_API = os.getenv("OPENAI_API")
CITY = "Ludhiana"

# -------- WEATHER --------
weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API}&units=metric"

weather_res = requests.get(weather_url)
weather_data = weather_res.json()

if weather_data.get("cod") != 200:
    print("Weather Error:", weather_data)
    temp = "N/A"
    weather = "N/A"
else:
    temp = weather_data["main"]["temp"]
    weather = weather_data["weather"][0]["description"]


# -------- NEWS --------
news_url = f"https://gnews.io/api/v4/top-headlines?country=in&lang=en&token={NEWS_API}"
news_res = requests.get(news_url)
news_data = news_res.json()

articles = []

if "articles" in news_data:
    articles = news_data["articles"][:8]
else:
    print("News Error:", news_data)


# -------- BUILD RAW NEWS (IMPORTANT UPGRADE) --------
raw_news = ""

for article in articles:
    raw_news += f"""
Title: {article['title']}
Description: {article['description']}
Source: {article['source']['name']}
"""


# -------- AI --------
client = OpenAI(api_key=OPENAI_API) 

prompt = f"""
You are my daily morning briefing assistant.

About me:
Jannat Kondal, 1st year CSE student.
I care about: coding, AI, startups, geopolitics, media, Indian tech ecosystem.

Your job:
Give me a HIGH-SIGNAL morning briefing. Not generic headlines.

Rules:
- Select the 5–6 MOST important stories (no fluff)
- Prioritize: AI, tech, startups, geopolitics, business, major global shifts
- Skip: entertainment, cricket, gossip unless extremely important

For EACH story:
• Bold headline  
• 3–5 sentence summary  
• Why it matters to me (specific to CSE/tech mindset)  
• “So what” → one clear takeaway  

Extra:
- Connect dots
- Be opinionated when needed
- Skip useless stories completely

Tone:
- Smart friend
- No corporate tone
- No fluff

Structure:
- Clean
- Scannable

Weather:
{temp}°C, {weather}

News:
{raw_news}
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

ai_output = response.choices[0].message.content

# -------- FINAL OUTPUT --------
print("\n\n===== MORNING BRIEFING =====\n")
print(ai_output)
# -------- EMAIL --------
EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

msg = MIMEText(ai_output)
msg["Subject"] = "Your Daily Morning Briefing ☀️"
msg["From"] = EMAIL
msg["To"] = EMAIL

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASSWORD)
        server.send_message(msg)
    print("Email sent successfully ✅")
except Exception as e:
    print("Email failed ❌", e)
