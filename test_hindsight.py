from utils.memory import (
    create_memory_bank,
    store_feedback,
    recall_feedback
)

print("Creating Hindsight memory bank...")

create_memory_bank()
print("Memory bank created!")

print("\nStoring sample feedback...")

store_feedback(
    "Customer C101 reported that food delivery was very late.",
    metadata={
        "customer_id": "C101",
        "issue": "delivery_delay"
    }
)

print("Feedback stored successfully!")

print("\nRecalling stored feedback...")

result = recall_feedback(
    "What problem did customer C101 report?"
)

for memory in result.results:
    print("-", memory.text)

print("\nHindsight integration test completed!")