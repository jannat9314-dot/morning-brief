import requests
import os
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText

# -------- CONFIG & API LOADING (CLEANED) --------
# We use .strip() to remove any accidental invisible spaces or newlines
WEATHER_API = os.getenv("WEATHER_API", "").strip()
NEWS_API = os.getenv("NEWS_API", "").strip()
OPENAI_API = os.getenv("OPENAI_API", "").strip()
EMAIL = os.getenv("EMAIL", "").strip()
APP_PASSWORD = os.getenv("APP_PASSWORD", "").strip()

CITY = "Ludhiana"

# -------- WEATHER --------
# Added a check to ensure API key exists before calling
if not WEATHER_API:
    print("Error: WEATHER_API key is missing from Environment Variables.")
    temp, weather = "N/A", "N/A"
else:
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API}&units=metric"
    try:
        weather_res = requests.get(weather_url)
        weather_data = weather_res.json()
        if weather_data.get("cod") != 200:
            print("Weather Error:", weather_data.get("message", "Unknown error"))
            temp, weather = "N/A", "N/A"
        else:
            temp = weather_data["main"]["temp"]
            weather = weather_data["weather"][0]["description"]
    except Exception as e:
        print(f"Weather Request Failed: {e}")
        temp, weather = "N/A", "N/A"

# -------- NEWS --------
articles = []
if not NEWS_API:
    print("Error: NEWS_API key is missing.")
else:
    news_url = f"https://gnews.io/api/v4/top-headlines?country=in&lang=en&token={NEWS_API}"
    try:
        news_res = requests.get(news_url)
        news_data = news_res.json()
        if "articles" in news_data:
            articles = news_data["articles"][:8]
        else:
            print("News Error:", news_data)
    except Exception as e:
        print(f"News Request Failed: {e}")

# -------- BUILD RAW NEWS --------
raw_news = ""
for article in articles:
    raw_news += f"\nTitle: {article['title']}\nDescription: {article['description']}\nSource: {article['source']['name']}\n"

# -------- AI --------
if not OPENAI_API:
    print("Error: OPENAI_API key is missing. Skipping AI generation.")
    ai_output = "AI Briefing could not be generated due to missing API key."
else:
    # Use the variable from the environment, NOT a hardcoded string
    client = OpenAI(api_key=OPENAI_API)

    prompt = f"""
    You are my daily morning briefing assistant.
    User: Jannat Kondal, 1st year CSE student.
    Interests: coding, AI, startups, geopolitics, Indian tech ecosystem.
    
    Current Weather in {CITY}: {temp}°C, {weather}
    
    Top News Stories:
    {raw_news}
    
    Task: Provide a high-signal, smart briefing. 5-6 stories. 
    Focus on "So what" for a CSE student. Bold headlines. No corporate fluff.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        ai_output = response.choices[0].message.content
    except Exception as e:
        ai_output = f"OpenAI Error: {e}"
        print(ai_output)

# -------- FINAL OUTPUT --------
print("\n===== MORNING BRIEFING =====\n")
print(ai_output)

# -------- EMAIL --------
if EMAIL and APP_PASSWORD:
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
else:
    print("Email skipped: EMAIL or APP_PASSWORD not set.")
    print("KEY CHECK:", OPENAI_API)