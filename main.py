import feedparser
import smtplib
import os
import openai
from email.message import EmailMessage

# --- EXPANDED STRATEGIC CONFIGURATION ---
RSS_FEEDS = [
    "https://aviationweek.com/awn-rss/feed",
    "https://www.flightglobal.com/news/rss",
    "https://evtol.com/feed/",
    "https://www.hydrogeninsight.com/rss",
    "https://electrek.co/category/batteries/feed/" # Added for Tech Triggers
]

# Strategic Keywords from the Three Games Framework
KEYWORDS = [
    # Game 1: AAM
    "BETA Technologies", "Joby Aviation", "Archer Aviation", "Wisk", "Electra.aero", "eVTOL", "Part 23",
    # Game 2: Regional
    "Heart Aerospace", "ZeroAvia", "Ampaire", "ES-30", "Pratt & Whitney", "Safran", "Embraer", "ATR", "Dash 8",
    # Game 3: Narrowbody & Tech Triggers
    "RISE", "Airbus ZEROe", "Rolls-Royce", "open-fan", "hydrogen fuel cell", "solid-state", "SiC", "Wh/kg", "2MW",
    # China Strategy
    "CATL", "BYD", "EHang", "AutoFlight", "CAAC"
]

# External VIP Assets (From your LinkedIn)
EXTERNAL_VIPS = {
    "Electra.aero": "Marc Allen (CEO)",
    "BETA Technologies": "Ryan Barta (Strategy)",
    "Wisk": "Dan Dalton (VP) / Daniela Schaff",
    "ZeroAvia": "Julieta Diederichsen (Dir. Biz Dev)",
    "Boeing": "Jim Hileman (VP Sustainability)",
    "United": "Lauren Riley (CSO)",
    "Embraer": "Daniel Moczydlower (CEO, Embraer-X)",
    "Safran": "Peter Detjen (VP Innovation)"
}

EMAIL_ADDRESS = "sfeinberg@gmail.com" 
RECIPIENTS = ["sfeinberg@gmail.com"]

def get_intelligence():
    print("Scraping external aviation and battery feeds...")
    collected_news = ""
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:25]:
            # Filter by Strategic Keywords
            if any(key.lower() in entry.title.lower() for key in KEYWORDS):
                # Check for External HUMINT Triggers
                humint_alert = ""
                for entity, contact in EXTERNAL_VIPS.items():
                    if entity.lower() in entry.title.lower():
                        humint_alert = f"📍 HUMINT ALERT: News regarding {entity}. Reach out to {contact} for external ground truth.\n"
                
                collected_news += f"{humint_alert}TITLE: {entry.title}\nLINK: {entry.link}\nSUMMARY: {entry.summary[:250]}...\n\n"
    return collected_news

def summarize_with_ai(raw_text):
    print("Generating Synthesis via 'Three Games' Framework...")
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = f"""
    You are the Strategic Intelligence Lead at GE Aerospace. 
    Review the following external news and summarize for leadership using the Three Games framework:
    - GAME 1 (AAM): Focus on certification (BETA/Joby/Wisk) and Part 23/135 updates.
    - GAME 2 (Regional): Identify any moves by Pratt/Safran/Embraer to lock out GE.
    - GAME 3 (Narrowbody/RISE): Focus on battery breakthroughs (Wh/kg) and Airbus ZEROe.
    - CHINA WATCH: Any evidence of CATL/BYD hitting 500 Wh/kg or EHang scaling.

    DATA:
    {raw_text}
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def send_intel_report(content):
    msg = EmailMessage()
    msg['Subject'] = f"EXTERNAL INTEL: Three Games Strategic Brief"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ", ".join(RECIPIENTS)
    msg.set_content(content)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, os.environ.get("EMAIL_PASSWORD"))
            smtp.send_message(msg)
            print("Intelligence Report Sent.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    news = get_intelligence()
    if news:
        # Use AI summary if key is available, else send raw
        final_report = summarize_with_ai(news) if os.environ.get("OPENAI_API_KEY") else news
        send_intel_report(final_report)
    else:
        print("No strategic external signals found.")
