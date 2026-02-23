import feedparser
import smtplib
import os
import openai
from email.message import EmailMessage

# --- CONFIGURATION ---
RSS_FEEDS = [
    "https://aviationweek.com/awn-rss/feed",
    "https://www.flightglobal.com/news/rss",
    "https://evtol.com/feed/",
    "https://simpleflying.com/feed/"
]

KEYWORDS = ["hybrid", "electric", "AAM", "eVTOL", "battery", "China", "RISE", "EPFD", "narrowbody", "hydrogen"]

# Update these to match your working test
EMAIL_ADDRESS = "sfeinberg@gmail.com" 
RECIPIENTS = "sfeinberg@gmail.com" 

def get_intelligence():
    print("Scraping aviation feeds...")
    collected_news = ""
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            # Only keep news that matches your strategic keywords
            if any(key.lower() in entry.title.lower() for key in KEYWORDS):
                collected_news += f"SOURCE: {entry.title}\nLINK: {entry.link}\nSUMMARY: {entry.summary[:300]}\n\n"
    return collected_news

def summarize_with_ai(raw_text):
    print("Generating Strategic Synthesis via OpenAI...")
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f"""
    You are a Lead Strategic Intelligence Analyst for GE Aerospace. 
    Review the following aviation news and write a concise, executive-level briefing.
    Focus on implications for GE's 2030 roadmap (RISE, hybrid-electric, narrowbody dominance).
    
    STRUCTURE:
    1. EXECUTIVE SIGNAL (The 'So What?' of the week)
    2. AAM & eVTOL VELOCITY (Focus on certification and China developments)
    3. PROPULSION & ENERGY (Battery, Hydrogen, and Thermal Mgmt breakthroughs)
    4. COMPETITIVE LANDSCAPE (Startups, funding, and partnership moves)

    DATA:
    {raw_text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o", # Or "gpt-4-turbo"
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_final_email(content):
    msg = EmailMessage()
    msg['Subject'] = "WEEKLY INTEL: Hybrid-Electric & AAM Strategy"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ", ".join(RECIPIENTS)
    msg.set_content(content)

    email_pass = os.environ.get("EMAIL_PASSWORD")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, email_pass)
            smtp.send_message(msg)
            print("Executive Intel Report Sent!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    raw_data = get_intelligence()
    
    if raw_data:
        # If you have OpenAI API key set up, use this:
        if os.environ.get("OPENAI_API_KEY"):
            final_report = summarize_with_ai(raw_data)
        else:
            final_report = "--- RAW INTEL REPORT ---\n\n" + raw_data
        
        send_final_email(final_report)
    else:
        print("No strategic news found this week. Skipping email.")
