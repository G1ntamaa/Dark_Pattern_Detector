import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np


PATTERNS = {
    "Urgency & Scarcity": {
        "description": "Creates false time pressure or fake low-stock warnings to rush purchases.",
        "color": "#FF4444",
        "icon": "",
        "keywords": [
            r"\bonly\s+\d+\s+left\b", r"\bhurry\b", r"\blimited\s+time\b",
            r"\bends?\s+in\b", r"\btoday\s+only\b", r"\blast\s+chance\b",
            r"\bflash\s+sale\b", r"\bexpires?\s+in\b", r"\bjust\s+\d+\s+remaining\b",
            r"\blow\s+stock\b", r"\bselling\s+fast\b", r"\bnearly\s+gone\b",
            r"\b\d+\s+sold\s+in\s+last\b", r"\bhigh\s+demand\b",
            r"\bdon't\s+miss\s+out\b", r"\bact\s+now\b", r"\btime\s+is\s+running\b",
            r"\bwhile\s+stocks?\s+last\b", r"\blimited\s+stock\b", r"\bscarce\b",
        ],
        "severity": "High",
    },
    "Misleading Discounts": {
        "description": "Inflated original prices, fake percentage-offs, or deceptive sale framing.",
        "color": "#FF8C00",
        "icon": "",
        "keywords": [
            r"\b\d{2,3}%\s+off\b", r"\bwas\s+₹[\d,]+\b", r"\bm\.r\.p\b",
            r"\bspecial\s+price\b", r"\bdeal\s+of\s+the\s+day\b",
            r"\bslashed\s+price\b", r"\bextra\s+\d+%\s+off\b",
            r"\bcoupon\s+applied\b", r"\bbankoffers?\b", r"\bno\s+cost\s+emi\b",
            r"\beffective\s+price\b", r"\bsave\s+₹[\d,]+\b",
            r"\bstrikethrough\b", r"\boriginal\s+price\b",
            r"\byou\s+save\b", r"\bbig\s+billion\b", r"\bgreat\s+indian\b",
        ],
        "severity": "High",
    },
    "Social Proof Manipulation": {
        "description": "Fake or exaggerated popularity signals to pressure buyers.",
        "color": "#9B59B6",
        "icon": "",
        "keywords": [
            r"\b\d+\s+people\s+(?:are\s+)?(?:viewing|looking at)\b",
            r"\bbest\s*seller\b", r"\b#1\s+(?:rated|selling|choice)\b",
            r"\btop\s+rated\b", r"\bmost\s+popular\b", r"\bcustomers?\s+also\s+bought\b",
            r"\bfrequently\s+bought\s+together\b", r"\bhighly\s+rated\b",
            r"\bverified\s+(?:buyer|purchase)\b", r"\b\d+\s+(?:ratings?|reviews?)\b",
            r"\brecommended\s+by\b", r"\btrending\b", r"\bviralling?\b",
        ],
        "severity": "Medium",
    },
    "Hidden Costs": {
        "description": "Extra charges revealed only at checkout or buried in fine print.",
        "color": "#E74C3C",
        "icon": "",
        "keywords": [
            r"\bconvenience\s+fee\b", r"\bhandling\s+charge\b",
            r"\bpackaging\s+fee\b", r"\bplatform\s+fee\b",
            r"\bservice\s+charge\b", r"\bdelivery\s+(?:charge|fee)\s+added\b",
            r"\btaxes?\s+(?:and\s+fees?\s+)?(?:not\s+)?included\b",
            r"\badditional\s+charge\b", r"\bextra\s+charge\b",
            r"\binstallation\s+fee\b", r"\bsurcharge\b",
            r"\bprocessing\s+fee\b", r"\bapplicable\s+taxes?\b",
        ],
        "severity": "High",
    },
    "Confirm Shaming": {
        "description": "Opt-out buttons written to make users feel guilty for declining.",
        "color": "#3498DB",
        "icon": "",
        "keywords": [
            r"\bno\s+thanks.*?(?:save|deal|discount|offer)\b",
            r"\bi\s+don'?t\s+want\b", r"\bno\s+i\s+don'?t\b",
            r"\bskip\s+(?:this\s+)?(?:great|amazing|exclusive)\b",
            r"\bi\s+prefer\s+(?:to\s+pay|full\s+price)\b",
            r"\bno\s+thanks.*?(?:protect|cover|insure)\b",
            r"\bdecline.*?(?:offer|discount|protection)\b",
            r"\bi\s+don'?t\s+need\s+(?:this|protection|coverage)\b",
        ],
        "severity": "Medium",
    },
    "Basket Sneaking": {
        "description": "Items or subscriptions added to cart without explicit user consent.",
        "color": "#1ABC9C",
        "icon": "",
        "keywords": [
            r"\badded\s+automatically\b", r"\bpre.?selected\b",
            r"\bincluded\s+(?:by\s+default|automatically)\b",
            r"\bopt\s+out\b", r"\buncheck\s+to\s+remove\b",
            r"\bauto.?renew\b", r"\bsubscription\s+included\b",
            r"\bprotection\s+plan\s+added\b", r"\bextended\s+warranty\s+added\b",
            r"\bdefault(?:ed)?\s+to\b", r"\byou'?ve\s+been\s+enrolled\b",
        ],
        "severity": "High",
    },
    "Disguised Ads": {
        "description": "Paid promotions styled to look like organic results or editorial content.",
        "color": "#F39C12",
        "icon": "",
        "keywords": [
            r"\bsponsored\b", r"\bad\b", r"\bpromoted\b",
            r"\bfeatured\s+(?:product|listing|brand)\b",
            r"\bpaid\s+(?:placement|promotion|partnership)\b",
            r"\baffiliate\b", r"\badvertisement\b",
            r"\bbranded\s+content\b", r"\bpartner\s+content\b",
        ],
        "severity": "Low",
    },
    "Trick Questions": {
        "description": "Double negatives or confusing language in opt-in/opt-out checkboxes.",
        "color": "#7F8C8D",
        "icon": "",
        "keywords": [
            r"\buncheck\s+if\s+you\s+(?:do\s+)?(?:not|don'?t)\b",
            r"\bcheck\s+if\s+you\s+don'?t\s+want\b",
            r"\btick\s+to\s+(?:not|stop)\b",
            r"\bdo\s+not\s+(?:un)?check\s+if\b",
            r"\bby\s+(?:not\s+)?checking\s+this\s+box\b",
            r"\bopt\s+(?:in|out)\s+of\s+(?:not\s+)?receiving\b",
        ],
        "severity": "Medium",
    },
}

#  Training Data for ML Model

TRAINING_DATA = [
    # Urgency & Scarcity
    ("Only 3 items left in stock!", "Urgency & Scarcity"),
    ("Hurry! Sale ends in 2 hours", "Urgency & Scarcity"),
    ("Limited time offer - today only", "Urgency & Scarcity"),
    ("Low stock alert: only 2 remaining", "Urgency & Scarcity"),
    ("Selling fast! 47 sold in last 24 hours", "Urgency & Scarcity"),
    ("Act now - offer expires tonight", "Urgency & Scarcity"),
    ("High demand! People keep buying this", "Urgency & Scarcity"),
    ("Last chance to grab this deal", "Urgency & Scarcity"),
    # Misleading Discounts
    ("Was ₹5999, now ₹599 - 90% off!", "Misleading Discounts"),
    ("MRP ₹2000, you pay ₹199 only", "Misleading Discounts"),
    ("Extra 10% off with bank offer", "Misleading Discounts"),
    ("Deal of the day - special price", "Misleading Discounts"),
    ("Effective price after cashback: ₹0", "Misleading Discounts"),
    ("Save ₹3000 on this product today", "Misleading Discounts"),
    # Social Proof
    ("142 people are viewing this right now", "Social Proof Manipulation"),
    ("Bestseller in Electronics category", "Social Proof Manipulation"),
    ("#1 rated product by customers", "Social Proof Manipulation"),
    ("4.5 stars from 12,483 verified buyers", "Social Proof Manipulation"),
    ("Customers also bought these items", "Social Proof Manipulation"),
    ("Trending - most popular this week", "Social Proof Manipulation"),
    # Hidden Costs
    ("Convenience fee: ₹49 added at checkout", "Hidden Costs"),
    ("Platform fee applicable on this order", "Hidden Costs"),
    ("Packaging charges: ₹29 extra", "Hidden Costs"),
    ("Taxes and fees not included in price", "Hidden Costs"),
    ("Service surcharge added to total", "Hidden Costs"),
    # Confirm Shaming
    ("No thanks, I don't want to save money", "Confirm Shaming"),
    ("I prefer to pay full price", "Confirm Shaming"),
    ("No I don't want free delivery", "Confirm Shaming"),
    ("Skip this great offer", "Confirm Shaming"),
    ("I don't need protection for my order", "Confirm Shaming"),
    # Basket Sneaking
    ("1-year protection plan added automatically", "Basket Sneaking"),
    ("Extended warranty pre-selected for you", "Basket Sneaking"),
    ("Uncheck to remove subscription", "Basket Sneaking"),
    ("Auto-renew enabled by default", "Basket Sneaking"),
    ("You've been enrolled in Prime", "Basket Sneaking"),
    # Neutral
    ("Product description: 6GB RAM, 128GB storage", "None"),
    ("Free delivery on orders above ₹499", "None"),
    ("30-day return policy available", "None"),
    ("Customer support: 24x7 available", "None"),
    ("Color options: Black, White, Blue", "None"),
    ("Compatible with Android and iOS", "None"),
    ("Warranty: 1 year manufacturer warranty", "None"),
    ("In the box: device, charger, manual", "None"),
]


@dataclass
class Detection:
    pattern_type: str
    matched_text: str
    severity: str
    color: str
    icon: str
    context: str = ""


@dataclass
class AnalysisResult:
    url: str
    page_title: str
    raw_text: str
    detections: List[Detection] = field(default_factory=list)
    score: int = 0
    category_counts: Dict[str, int] = field(default_factory=dict)
    verdict: str = ""

#  ML Pipeline

class DarkPatternML:
    def __init__(self):
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 3), max_features=5000)),
            ("clf", LogisticRegression(max_iter=500, C=1.0)),
        ])
        self._train()

    def _train(self):
        texts = [x[0] for x in TRAINING_DATA]
        labels = [x[1] for x in TRAINING_DATA]
        self.pipeline.fit(texts, labels)

    def predict(self, text: str) -> Tuple[str, float]:
        pred = self.pipeline.predict([text])[0]
        proba = self.pipeline.predict_proba([text])[0]
        confidence = max(proba)
        return pred, confidence

#  Rule-Based Detector

def rule_based_detect(text: str) -> List[Detection]:
    detections = []
    text_lower = text.lower()

    for pattern_name, config in PATTERNS.items():
        for keyword_regex in config["keywords"]:
            matches = re.finditer(keyword_regex, text_lower, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                context = "..." + text[start:end].strip() + "..."
                detections.append(Detection(
                    pattern_type=pattern_name,
                    matched_text=match.group(),
                    severity=config["severity"],
                    color=config["color"],
                    icon=config["icon"],
                    context=context,
                ))
    return detections

#  Main Analyzer

class DarkPatternAnalyzer:
    def __init__(self):
        self.ml_model = DarkPatternML()

    def analyze_text(self, text: str, url: str = "Manual Input", title: str = "Pasted Content") -> AnalysisResult:
        result = AnalysisResult(url=url, page_title=title, raw_text=text)

        # Rule-based detection
        rule_detections = rule_based_detect(text)

        # ML detection on sentences
        sentences = [s.strip() for s in re.split(r'[.!?\n]', text) if len(s.strip()) > 15]
        ml_detections = []
        for sentence in sentences:
            label, confidence = self.ml_model.predict(sentence)
            if label != "None" and confidence > 0.55:
                config = PATTERNS.get(label, {})
                ml_detections.append(Detection(
                    pattern_type=label,
                    matched_text=sentence[:80],
                    severity=config.get("severity", "Medium"),
                    color=config.get("color", "#888"),
                    icon=config.get("icon", "⚠️"),
                    context=sentence,
                ))

        # Merge and deduplicate
        all_detections = rule_detections + ml_detections
        seen = set()
        unique = []
        for d in all_detections:
            key = (d.pattern_type, d.matched_text[:30].lower())
            if key not in seen:
                seen.add(key)
                unique.append(d)

        result.detections = unique

        # Category counts
        for d in unique:
            result.category_counts[d.pattern_type] = result.category_counts.get(d.pattern_type, 0) + 1

        # Score (0–100)
        severity_weights = {"High": 15, "Medium": 8, "Low": 3}
        raw_score = sum(severity_weights.get(d.severity, 5) for d in unique)
        result.score = min(100, raw_score)

        # Verdict
        if result.score == 0:
            result.verdict = "✅ Clean"
        elif result.score <= 20:
            result.verdict = "🟡 Mildly Deceptive"
        elif result.score <= 50:
            result.verdict = "🟠 Moderately Deceptive"
        else:
            result.verdict = "🔴 Highly Deceptive"

        return result

    def get_summary_df(self, result: AnalysisResult) -> pd.DataFrame:
        if not result.detections:
            return pd.DataFrame()
        rows = [{
            "Pattern Type": d.pattern_type,
            "Severity": d.severity,
            "Matched Text": d.matched_text,
            "Context": d.context,
        } for d in result.detections]
        return pd.DataFrame(rows)
