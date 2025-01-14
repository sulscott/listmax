import json
from app import lambda_handler

# Load the event from a file
with open('../events/twilio_message.json', 'r') as f:
    mock_event = json.load(f)

response = lambda_handler(mock_event, None)
print(response)