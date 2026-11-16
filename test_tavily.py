import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
results = client.search("Who is the CEO of Twitter?", max_results=3)

for r in results["results"]:
    print(r["title"])
    print(r["url"])
    print("---")