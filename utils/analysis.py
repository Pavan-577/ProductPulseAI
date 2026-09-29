import pandas as pd
import re


# --------------------------------
# 1. SENTIMENT ANALYSIS
# --------------------------------

def analyze_sentiment(feedback):
    """Classify feedback as Positive, Negative, or Neutral."""

    text = str(feedback).lower()

    positive_words = [
        "excellent", "good", "great", "fast",
        "perfect", "perfectly", "improved", "easy",
        "love", "amazing", "smooth", "wonderful",
        "helpful", "satisfied", "quick", "reliable",
        "working well", "on time", "delicious"
    ]

    negative_words = [
        "late", "slow", "cold", "wrong", "problem",
        "bad", "poor", "delay", "issue", "inaccurate",
        "failed", "failure", "broken", "crash",
        "crashing", "not working", "terrible",
        "disappointed", "missing", "damaged",
        "unhappy", "stale", "overpriced", "unacceptable"
    ]

    positive_count = sum(
        1 for word in positive_words if word in text
    )

    negative_count = sum(
        1 for word in negative_words if word in text
    )

    # Handle common negative phrases
    if any(phrase in text for phrase in [
        "not good", "not great", "not satisfied",
        "not happy", "not helpful", "not reliable",
        "not working", "never works", "doesn't work",
        "does not work", "not on time"
    ]):
        negative_count += 2

    if negative_count > positive_count:
        return "Negative"

    elif positive_count > negative_count:
        return "Positive"

    else:
        return "Neutral"


# --------------------------------
# 2. ISSUE DETECTION
# --------------------------------

ISSUE_KEYWORDS = {
    "Tracking Issues": [
        "track", "tracking", "location",
        "live status", "order status",
        "track order", "order tracking"
    ],

    "Delivery Delays": [
        "late", "delay", "delayed",
        "delivery time", "arrived late",
        "not delivered", "waiting for delivery",
        "slow delivery", "delivery took"
    ],

    "Food Quality": [
        "cold", "stale", "tasteless",
        "spoiled", "undercooked", "overcooked",
        "bad taste", "food quality",
        "unfresh", "rotten", "food was bad"
    ],

    "App Experience": [
        "app", "crash", "crashing",
        "freeze", "freezing", "loading",
        "interface", "login", "logged out",
        "screen", "navigation", "bug",
        "slow application"
    ],

    "Payment Issues": [
        "payment", "paid", "refund",
        "transaction", "billing", "charged",
        "money deducted", "payment failed",
        "double charged", "upi",
        "payment error", "wrong amount"
    ],

    "Order Issues": [
        "wrong order", "wrong item",
        "missing item", "missing items",
        "order cancelled", "canceled",
        "order missing", "incorrect order",
        "incomplete order", "item missing"
    ],

    "Customer Support": [
        "customer support", "customer service",
        "support team", "help center",
        "no response", "rude staff",
        "support agent", "complaint"
    ],

    "Packaging Issues": [
        "packaging", "package damaged",
        "leaking", "leaked", "spilled",
        "broken package", "poor packaging",
        "container broken"
    ],

    "Pricing Issues": [
        "expensive", "overpriced",
        "high price", "extra charge",
        "hidden charges", "price",
        "discount", "coupon", "offer"
    ],

    "Other": []
}


def detect_issue(feedback):
    """Identify the main issue using keyword rules."""

    text = str(feedback).lower()

    # More specific categories are checked first.
    priority = [
        "Tracking Issues",
        "Payment Issues",
        "Order Issues",
        "Packaging Issues",
        "Delivery Delays",
        "Food Quality",
        "Customer Support",
        "Pricing Issues",
        "App Experience"
    ]

    for issue in priority:
        for keyword in ISSUE_KEYWORDS[issue]:
            if keyword in text:
                return issue

    return "Other"


# --------------------------------
# 3. COMPLETE FEEDBACK ANALYSIS
# --------------------------------

def analyze_feedback(df):
    """Analyze feedback and return an updated DataFrame."""

    df = df.copy()

    if "feedback" not in df.columns:
        raise ValueError(
            "CSV must contain a 'feedback' column."
        )

    df["feedback"] = df["feedback"].fillna("").astype(str)

    df["sentiment"] = df["feedback"].apply(
        analyze_sentiment
    )

    df["issue"] = df["feedback"].apply(
        detect_issue
    )

    return df