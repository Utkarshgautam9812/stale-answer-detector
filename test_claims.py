import json
from claims import extract_claims

answer = (
    "Twitter's CEO is Jack Dorsey, and the platform is still called Twitter. "
    "ChatGPT Plus costs $20 per month. Paris is the capital of France."
)

print(json.dumps(extract_claims(answer), indent=2))