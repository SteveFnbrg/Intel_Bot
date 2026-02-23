import feedparser
import smtplib
import os
import openai
from datetime import datetime, timedelta
from email.message import EmailMessage

# --- EXECUTIVE STRATEGIC CONFIGURATION ---
RSS_FEEDS = [
    "https://aviationweek.com/awn-rss/feed",
    "https://www.flightglobal.com/news/rss",
    "https://evtol.com/feed/",
    "https://www.hydrogeninsight.com/rss",
    "https://electrek.co/category/batteries/feed/"
]

# Keywords derived from your "Three Games" Strategic Assessment
KEYWORDS = [
    "BETA Technologies", "Joby", "Archer Aviation", "Wisk", "Electra.aero",  # Game 1
    "Heart Aerospace", "ZeroAvia", "Ampaire", "ES-30", "Embraer", "Safran", # Game 2
    "Airbus ZEROe", "Rolls-Royce", "solid-state", "SiC", "Wh/kg", "2MW",     # Game 3
    "CATL", "BYD", "EHang", "AutoFlight", "CAAC"                            # China
]

# External VIP Assets (From your LinkedIn) - Only External
EXTERNAL_VIPS = {
    "Electra.aero": "Marc Allen (CEO)",
    "BETA Technologies": "Ryan Barta (Strategy)",
    "Wisk": "Dan Dalton (VP)",
    "ZeroAvia": "Julieta Diederichsen (Dir. Biz Dev)",
    "United": "Lauren Riley (CSO)",
    "Boeing": "Jim Hileman (VP Sustainability)",
    "Safran": "Peter Detjen (VP Innovation)"
}

def get_30_day_intel():
    print("Scraping for 30-day signal...")
    thirty_days_ago = datetime.now() - timedelta(days=30)
    collected_news = ""
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Date Check
            dt = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else None
            if dt and dt < thirty_days_ago:
                continue
            
            # Keyword/Signal Check
            if any(key.lower() in entry.title.lower() for key in KEYWORDS):
                # Check for External HUMINT Triggers
                humint = ""
                for entity, contact in EXTERNAL_VIPS.items():
                    if entity.lower() in entry.title.lower():
                        humint = f"[EXTERNAL HUMINT: Reach out to {contact}] "
                
                collected_news += f"{humint}Source: {entry.title} ({dt.strftime('%b %d')})\nLink: {entry.link}\n\n"
    
    return collected_news

def summarize_ruthlessly(raw_text):
    print("Synthesizing Signal...")
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # This prompt is the 'Executive Filter'
    prompt = f"""
    You are the Lead Strategic Intelligence Analyst for GE Aerospace. 
    Review the news items from the last 30 days and provide a high-signal briefing.
    
    CRITICAL RULES:
    1. ZERO FLUFF: Do not use phrases like "There were no updates regarding..."
    2. OMIT EMPTY SECTIONS: If a 'Game' has no news, skip that section entirely.
    3. SO WHAT: Focus on how this impacts the 'Three Games' roadmap.
    4. HUMINT: If an external connection is mentioned, highlight the 'Ground Truth' opportunity.

    STRUCTURE:
    - **Executive Summary** (Top 3 impacts only)
    - **Strategic Shifts** (Organize by Game 1, 2, or 3 ONLY if there is news)
    - **China Watch** (Only if technical/regulatory signal exists)

    DATA:
    {raw_text}
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_intel(content):
    msg = EmailMessage()
    msg['Subject'] = f"SIGNAL: Strategic Intel Brief ({datetime.now().strftime('%b %d')})"
    msg['From'] = "your-email@gmail.com"
    msg['To'] = "your-email@gmail.com"
    msg.set_content(content)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("your-email@gmail.com", os.environ.get("EMAIL_PASSWORD"))
            smtp.send_message(msg)
            print("Executive Briefing Sent.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    signal = get_30_day_intel()
    if signal:
        briefing = summarize_ruthlessly(signal) if os.environ.get("OPENAI_API_KEY") else signal
        send_intel(briefing)
    else:
        # Instead of a full email, just log that it was a quiet week
        print("Zero signal detected in the last 30 days. No email sent.")
