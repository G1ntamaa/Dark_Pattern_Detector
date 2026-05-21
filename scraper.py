import requests
from bs4 import BeautifulSoup
import re
from typing import Tuple


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Selectors to extract relevant page sections
ECOM_SELECTORS = [
    "#productTitle", "#priceblock_ourprice", "#priceblock_dealprice",
    ".a-price", ".a-color-price", "#availability", "#almWidget",
    ".deal-countdown", "#couponBadgeRegularVpc", "#buybox",
    "#productOverview_feature_div", "#feature-bullets", "#acrPopover",
    ".rush-component", "#urgency-message", "#social-proofing-faceout-title-tk",
    # Flipkart
    "._30jeq3", "._16Jk6d", "._1AtVbE", "._3pLy-c", "._1fQZEK",
    ".X_HDoN", "._3YhLQA", "._2p6lqe", "._1mXcCf", "._2kHMtA",
    # General
    "[class*='price']", "[class*='discount']", "[class*='offer']",
    "[class*='deal']", "[class*='urgency']", "[class*='scarcity']",
    "[class*='stock']", "[class*='timer']", "[class*='countdown']",
    "[class*='review']", "[class*='rating']", "[class*='badge']",
    "h1", "h2", ".product-title", ".product-price",
]


def scrape_page(url: str) -> Tuple[str, str, bool]:
    """
    Returns (text_content, page_title, success)
    """
    try:
        session = requests.Session()
        response = session.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Remove scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "meta"]):
            tag.decompose()

        # Page title
        title = soup.title.get_text(strip=True) if soup.title else "Unknown Page"

        # Try targeted selectors first
        targeted_texts = []
        for sel in ECOM_SELECTORS:
            elements = soup.select(sel)
            for el in elements:
                t = el.get_text(separator=" ", strip=True)
                if t and len(t) > 3:
                    targeted_texts.append(t)

        # Fallback: body text
        body_text = soup.get_text(separator="\n", strip=True)

        # Combine
        combined = "\n".join(targeted_texts) + "\n" + body_text

        # Clean up excessive whitespace
        combined = re.sub(r'\n{3,}', '\n\n', combined)
        combined = re.sub(r' {2,}', ' ', combined)

        return combined[:8000], title, True

    except requests.exceptions.SSLError:
        return "", "SSL Error - try with http://", False
    except requests.exceptions.ConnectionError:
        return "", "Connection failed - check URL or try pasting text manually", False
    except requests.exceptions.Timeout:
        return "", "Request timed out - page too slow", False
    except requests.exceptions.HTTPError as e:
        return "", f"HTTP {e.response.status_code} - page blocked scraping", False
    except Exception as e:
        return "", f"Error: {str(e)}", False


# ─────────────────────────────────────────────
#  Demo samples for offline testing
# ─────────────────────────────────────────────

DEMO_SAMPLES = {
    "Amazon-style Listing (High Deception)": """
    Wireless Bluetooth Earbuds Pro Max
    ₹599  MRP: ₹4,999  (88% off)
    Deal of the Day | Extra 10% off with HDFC Bank Card
    Save ₹4,400 today only!
    
    ⚡ Only 3 left in stock - order soon!
    Selling fast! 238 sold in last 24 hours
    🔥 147 people are viewing this right now
    
    Add Protection Plan (1 year) ✓ Pre-selected - ₹149
    Uncheck to remove warranty coverage
    
    FREE Delivery by Tomorrow - if you order in next 2 hours 14 minutes
    
    ⭐⭐⭐⭐⭐ #1 Best Seller in True Wireless Earbuds
    4.3 out of 5 stars (47,291 ratings)
    
    Customers also bought: Charging case (₹899), Ear tips pack (₹199)
    
    [BUY NOW]  [No thanks, I don't want free delivery]
    
    Platform fee: ₹29 applicable. Packaging charges extra.
    """,

    "Flipkart-style Listing (Medium Deception)": """
    Samsung Galaxy M34 5G
    ₹14,999  ₹22,999  35% off
    Extra 5% Cashback on Axis Bank Card
    Effective price: ₹13,499 after cashback
    
    ✅ Bestseller in Smartphones
    4.2 ★ (92,341 ratings)
    
    Only 10 left! High Demand Product.
    Big Billion Days Sale - Ends Tonight!
    
    Exchange Offer: Up to ₹8,000 off on exchange
    EMI from ₹791/month - No cost EMI available
    
    Free delivery above ₹499
    7-day replacement policy
    1 year manufacturer warranty
    """,

    "Clean Product Page (No Dark Patterns)": """
    Havells Wall Fan 300mm
    ₹1,850
    
    Color: Ivory White
    Speed Settings: 3 speeds
    Power: 55W
    
    Warranty: 2 years manufacturer warranty
    In the Box: 1 Fan, Mounting Hardware, User Manual
    
    Customer Reviews: 4.1 out of 5 (2,340 reviews)
    
    Free delivery on orders above ₹500
    30-day return policy
    Customer support available 9AM–6PM
    
    Product Description:
    Suitable for rooms up to 120 sq ft.
    Energy efficient motor with thermal overload protection.
    Compatible with standard Indian voltage (220V-240V).
    """,
}
