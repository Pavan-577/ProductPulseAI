
import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

# Load API credentials
load_dotenv()

API_URL = os.getenv(
    "HINDSIGHT_API_URL",
    "https://api.hindsight.vectorize.io"
)

API_KEY = os.getenv("HINDSIGHT_API_KEY")

# Fixed memory bank for ProductPulse AI
BANK_ID = "productpulse-feedback"


def get_client():
    """Connect to Hindsight Cloud."""

    if not API_KEY:
        raise ValueError(
            "HINDSIGHT_API_KEY missing. Check your .env file."
        )

    return Hindsight(
        base_url=API_URL,
        api_key=API_KEY
    )


def create_memory_bank():
    """Create a memory bank for customer feedback."""

    client = get_client()

    return client.create_bank(
        bank_id=BANK_ID,
        name="ProductPulse Customer Feedback"
    )


def store_feedback(feedback_text, metadata=None):
    """Store customer feedback in Hindsight memory."""

    client = get_client()

    return client.retain(
        bank_id=BANK_ID,
        content=feedback_text,
        context="Customer feedback analysis",
        metadata=metadata or {}
    )


def recall_feedback(query):
    """Retrieve relevant memories from Hindsight."""

    client = get_client()

    return client.recall(
        bank_id=BANK_ID,
        query=query
    )