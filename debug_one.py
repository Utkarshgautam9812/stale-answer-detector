from datetime import date
from claims import extract_claims
from verify import search_web, verify_claim

text = "The most recent men's FIFA World Cup was held in Qatar in 2022."

claims = extract_claims(text)
print("EXTRACTED:", claims)

for c in claims:
    sources = search_web(c["claim"])
    print("\nSOURCES FOUND:")
    for s in sources:
        print("-", s["title"], "|", s["url"])
    print("\nVERDICT:", verify_claim(c["claim"], sources, date.today().isoformat()))