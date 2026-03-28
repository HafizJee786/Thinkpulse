from app.agent import research_topic

print("Testing AI Research Assistant...")
print("=" * 50)

result = research_topic("Artificial Intelligence in Healthcare", depth="quick")

print(f"Topic: {result['topic']}")
print(f"Status: {result['status']}")
print(f"\nReport:\n{result['report']}")