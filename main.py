import feedparser
import smtplib
import os
from email.message import EmailMessage
import openai # pip install openai

# 1. Configuration - Sources for Aero Intel
FEEDS = [
    "https://aviationweek.com/awn-rss/feed",
    "https://www.flightglobal.com/news/rss",
    "https://simpleflying.com/feed/",
    "https://evtol.com/feed/"
]

KEYWORDS = ["hybrid", "electric", "AAM", "eVTOL", "battery", "China", "hydrogen", "narrowbody"]

def get_filtered_news():
    intel_dump = ""
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]: # Check recent items
            if any(key.lower() in entry.title.lower() for key in KEYWORDS):
                intel_dump += f"Title: {entry.title}\nSource: {entry.link}\nSummary: {entry.summary[:200]}\n\n"
    return intel_dump

def summarize_with_ai(raw_intel):
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"""
    You are a Strategic Intelligence Analyst for GE Aerospace. 
    Summarize the following raw news into a weekly intel brief.
    Format it with these sections:
    1. Executive Signal (Top 3 takeaways)
    2. Hybrid & Narrowbody (RISE/EPFD focus)
    3. China Intelligence
    4. Tech & Battery
    
    Raw Data:
    {raw_intel}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_intel_email(body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = f"GE Aero Strategy Brief: Hybrid-Electric Intel"
    msg['From'] = "your-intel-bot@gmail.com"
    msg['To'] = "sfeinberg@gmail.com" # Your key contacts

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("sfeinberg@gmail.com", os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)

if __name__ == "__main__":
    raw = get_filtered_news()
    if raw:
        # brief = summarize_with_ai(raw) # Uncomment if using OpenAI
        send_intel_email(raw) # For now, sends raw; swap for 'brief' once API is set
