import streamlit as st
import pandas as pd
import feedparser
from datetime import datetime, timedelta, timezone
import os

st.set_page_config(
    page_title="Paint Industry News Tracker",
    page_icon="📰",
    layout="wide"
)

CSV_PATH = "news_cache.csv"

RSS_FEEDS = {
    # Business & Economy
    "Enterprise Press": "https://enterprise.press/feed/",
    "Al Mal News": "https://www.almalnews.com/feed/",
    "Amwal Al Ghad": "https://amwalalghad.com/feed/",
    "Mubasher Info (English)": "https://english.mubasher.info/rss/",
    "Mubasher Info (Arabic)": "https://arabic.mubasher.info/rss/",
    "Daily News Egypt": "https://www.dailynewsegypt.com/feed/",
    "Egypt Independent": "https://www.egyptindependent.com/feed/",
    "Business Today Egypt": "https://www.businesstodayegypt.com/rss/",
    "Masrawy Economy": "https://www.masrawy.com/rss/SectionRSS?secId=100204",
    "Al Borsa News": "https://alborsanews.com/feed",
    "Al Dostor Economy": "https://www.dostor.org/rss.aspx?SecId=4",
    "Akhbar El Yom Economy": "https://akhbarelyom.com/rss?sectionId=69",
    "Al Watan Economy": "https://www.elwatannews.com/rss/section/77",
    "Youm7 Economy": "https://www.youm7.com/rss/SectionRss?SectionID=297",
    "Sada Elbalad Economy": "https://www.elbalad.news/rss.aspx?sectionid=22",
    "Al Ahram Economy": "https://gate.ahram.org.eg/rss/96.aspx",
    "El Fagr Economy": "https://www.elfagr.org/rss/sections/24",
    "Veto Gate Economy": "https://www.vetogate.com/rss/Section/3",
    "Cairo 24 Economy": "https://www.cairo24.com/rss/Section/5",
    "Masrawy Real Estate": "https://www.masrawy.com/rss/SectionRSS?secId=100209",
    # Construction & Real Estate
    "Construction Week Online ME": "https://www.constructionweekonline.com/rss",
    "Al Bawaba Real Estate": "https://www.albawabhnews.com/rss/section/18",
    "Al Masdar Real Estate": "https://almasdar.com/rss/section/6",
    # General News (for broader coverage)
    "Al Ahram": "https://gate.ahram.org.eg/rss/",
    "Al Masry Al Youm": "https://www.almasryalyoum.com/rss/rssfeeds",
    "Youm7": "https://www.youm7.com/rss/SectionRss?SectionID=65",
    "Sada Elbalad": "https://www.elbalad.news/rss.aspx",
    "El Watan": "https://www.elwatannews.com/rss/",
    "Masr Alarabia": "https://www.masralarabia.com/rss",
    "Mada Masr": "https://www.madamasr.com/en/feed",
    "Masress": "https://masress.com/en/rss"
}

# One-word, market-research-relevant keywords for the Egyptian paint market
CATEGORIES = {
    "Brands": [
        "National", "ناشيونال", "GLC", "جى", "باكين", "Pachin", "سايبس", "Sipes", "سكيب", "Scib", "ميدو", "Mido"
    ],
    "Products": [
        "دهان", "paint", "طلاء", "enamel", "epoxy", "إيبوكسي", "acrylic", "أكريليك", "ورنيش", "varnish"
    ],
    "Materials": [
        "pigment", "صبغة", "راتنج", "resin", "solvent", "مذيب", "titanium", "تيتانيوم", "oxide", "أكسيد"
    ],
    "Construction": [
        "بناء", "construction", "عقارات", "real", "estate", "إسكان", "infrastructure", "بنية", "مشروع", "project"
    ],
    "Automotive": [
        "سيارة", "car", "automotive", "مركبة", "vehicle", "طلاء", "دهان"
    ],
    "Regulation": [
        "قانون", "regulation", "معيار", "standard", "مواصفة", "specification", "VOC", "وزارة", "ministry"
    ],
    "Innovation": [
        "ابتكار", "innovation", "تطوير", "development", "بحث", "research", "تقنية", "technology", "صديق", "eco"
    ],
    "Trends": [
        "موضة", "trend", "ألوان", "color", "ديكور", "design", "سوق", "market", "طلب", "demand"
    ]
}

def parse_datetime(entry):
    # Always return timezone-aware UTC datetime
    for key in ["published_parsed", "updated_parsed"]:
        if key in entry and entry[key]:
            try:
                return datetime(*entry[key][:6], tzinfo=timezone.utc)
            except Exception:
                continue
    for key in ["published", "updated"]:
        if key in entry and entry[key]:
            try:
                dt = pd.to_datetime(entry[key], utc=True)
                return dt.to_pydatetime()
            except Exception:
                continue
    return datetime.now(timezone.utc)

def fetch_rss_news(keywords, days_back=180):
    results = []
    time_limit = datetime.now(timezone.utc) - timedelta(days=days_back)
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            published_dt = parse_datetime(entry)
            if published_dt < time_limit:
                continue
            content = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
            if any(kw.lower() in content for kw in keywords):
                results.append({
                    "timestamp": published_dt,
                    "keyword": "(rss)",
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                    "source": source
                })
    return results

def load_or_create_cache():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(columns=["timestamp", "keyword", "title", "summary", "link", "source"])
        df.to_csv(CSV_PATH, index=False)
        return df

st.title("📰 Paint Industry News Tracker")
st.markdown("""
Get the latest Egyptian paint market news using simple, powerful one-word keywords in English & Arabic.
Select a category and click 'Fetch Latest News' to see real-time results.
""")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("News Categories")
    category = st.selectbox("Select a category", list(CATEGORIES.keys()))
    st.caption("Keywords for this category:")
    for keyword in CATEGORIES[category]:
        st.markdown(f"• {keyword}")

    days_back = st.slider("Days to look back", min_value=7, max_value=180, value=180, step=7)

    if st.button("🔍 Fetch Latest News", use_container_width=True):
        news_cache = load_or_create_cache()
        new_entries = []

        with st.spinner("Scanning Egyptian RSS feeds..."):
            rss_items = fetch_rss_news(CATEGORIES[category], days_back)
            for item in rss_items:
                if news_cache.empty or not ((news_cache["title"] == item["title"]).any()):
                    new_entries.append(item)

            if new_entries:
                new_df = pd.DataFrame(new_entries)
                updated_cache = pd.concat([news_cache, new_df], ignore_index=True)
                updated_cache.to_csv(CSV_PATH, index=False)
                st.success(f"✅ Found {len(new_entries)} new articles")
            else:
                st.info("No new news found for these keywords")

    if st.button("🗑️ Clear News", help="Delete all cached news and reset the display"):
        if os.path.exists(CSV_PATH):
            os.remove(CSV_PATH)
        st.success("All news has been cleared.")
        st.experimental_rerun()

with col2:
    st.subheader("Latest Industry News")
    news_cache = load_or_create_cache()
    if not news_cache.empty:
        show_all = st.checkbox("Show all categories", value=False)
        filtered_news = news_cache if show_all else news_cache[news_cache["keyword"] == "(rss)"]
        if 'timestamp' in filtered_news.columns:
            filtered_news['timestamp'] = pd.to_datetime(filtered_news['timestamp'], errors='coerce')
            filtered_news = filtered_news.sort_values("timestamp", ascending=False)

        with st.container():
            for _, item in filtered_news.iterrows():
                with st.expander(f"📄 {item['title']}"):
                    st.markdown(f"**Source:** {item.get('source', 'Unknown')}")
                    st.markdown(f"**Published:** {item['timestamp']}")
                    st.markdown(item['summary'] if pd.notnull(item['summary']) else "No summary available")
                    st.markdown(f"[Read full article]({item['link']})")
    else:
        st.info("No news items yet. Click 'Fetch Latest News' to get started.")

st.divider()
col1, col2 = st.columns([3, 1])
with col1:
    st.caption("© 2025 Paint Industry News Tracker – Bilingual MVP")
with col2:
    if not news_cache.empty:
        csv = news_cache.to_csv(index=False)
        st.download_button("📥 Export Data", csv, "paint_news.csv", "text/csv")

st.sidebar.title("Feeds Status")
st.sidebar.success("✅ Egyptian RSS feeds active")
st.sidebar.markdown("*Powered by one-word market research keywords for Egypt*")
st.sidebar.markdown("**Note:** This is a prototype. For full functionality, please contact us.")