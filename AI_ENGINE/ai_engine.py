import re
from difflib import SequenceMatcher

# 🚫 Blocked Categories & Target Keywords Dataset
BLOCKED_KEYWORDS = {
    "social_media": [
        "snapchat", "facebook", "instagram", "tiktok", "twitter", "x", 
        "youtube", "reddit", "whatsapp", "telegram"
    ],
    "gaming": [
        "pubg", "freefire", "roblox", "steam", "minecraft", "epicgames"
    ],
    "phishing_and_malicious": [
        "free-recharge", "claim-bonus", "login-verify", "bank-update", 
        "account-security-alert", "free-coins", "win-prize"
    ]
}

def normalize_text(text):
    """
    User URL or Search Query ni normalize chestundhi (Spaces, symbols, query params ni clean chestundhi)
    Examples:
    - 'snap chat' -> 'snapchat'
    - 'google.com/search?q=snapchat+login' -> 'snapchatlogin'
    """
    if not text:
        return ""
    
    text = text.lower().strip()
    
    # Search Engine Query Parameters extraction (?q= or search=)
    if "q=" in text:
        text = text.split("q=")[-1].split("&")[0]
    elif "search=" in text:
        text = text.split("search=")[-1].split("&")[0]
    
    # Remove protocol prefix, domain extensions, spaces, and special symbols
    text = re.sub(r'https?://|www\.|[_\-+%20\s\.\/]', '', text)
    return text

def inspect_traffic_ai(url_or_query):
    """
    Core AI Decision Engine:
    Exact match kaakapoina ('snap chat', 'snapchat login', 'snap-chat-online') 
    base keyword ni capture chesi instant Block decision isthundhi.
    """
    if not url_or_query:
        return {
            "action": "ALLOW",
            "decision": "CONNECTED",
            "category": "General Traffic"
        }

    clean_input = normalize_text(url_or_query)
    raw_input = url_or_query.lower()

    for category, keywords in BLOCKED_KEYWORDS.items():
        for kw in keywords:
            # 1. Direct Pattern & Substring Matching
            if kw in clean_input or kw in raw_input:
                category_name = category.replace('_', ' ').title()
                return {
                    "action": "BLOCK",
                    "decision": f"AI BLOCKED ({category_name} Keyword)",
                    "category": category_name
                }
            
            # 2. Fuzzy Similarity Matching (Spelling variation handling)
            similarity = SequenceMatcher(None, kw, clean_input).ratio()
            if len(clean_input) >= 4 and similarity > 0.72:
                category_name = category.replace('_', ' ').title()
                return {
                    "action": "BLOCK",
                    "decision": f"AI BLOCKED (Fuzzy Pattern Match)",
                    "category": category_name
                }

    return {
        "action": "ALLOW",
        "decision": "CONNECTED",
        "category": "General Traffic"
    }