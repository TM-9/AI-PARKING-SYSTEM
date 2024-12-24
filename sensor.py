import random
import logging
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def detect_entry_exit(probability_entry=0.5):
    action = 'entry' if random.random() < probability_entry else 'exit'
    return action

# Simulate data collection
data = [detect_entry_exit(probability_entry=0.6) for _ in range(1000)]

# Analyze patterns
action_counts = Counter(data)
logging.info(f"Simulation Results: {action_counts}")

# Predictive rule (basic AI logic)
if action_counts['entry'] > action_counts['exit']:
    prediction = "Expect more entries"
else:
    prediction = "Expect more exits"

logging.info(f"Prediction based on simulation: {prediction}")
