import argparse
import requests
from bs4 import BeautifulSoup

# Simple in-memory cache
cache = {}

def make_request(url, content_type='html'):
    if url in cache:
        return cache[url]

    response = requests.get(url)
    try:
        if content_type == 'json':
            data = response.json()
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            data = soup.get_text()
    except ValueError:  # JSONDecodeError in newer versions of requests library
        # If JSON decoding fails, treat the response as HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.get_text()
    cache[url] = data
    return data

def search(term):
    search_url = f"https://www.google.md/search?q={term}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print("\nTop 10 Responses\n---------------------------------------------------------------------")
    # Extract top 10 results and print them
    for i, result in enumerate(soup.find_all('a')[16:26], start=1):
        print(f"{i}. {result.text} - {result['href']}")
        print("---------------------------------------------------------------------")
        
def main():
    parser = argparse.ArgumentParser(description="CLI program for making HTTP requests and displaying responses")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--url", help="Make an HTTP request to the specified URL")
    group.add_argument("-s", "--search", help="Make an HTTP request to search the term using your favorite search engine")
    parser.add_argument("-j", "--json", action="store_true", help="Request JSON content instead of HTML")

    args = parser.parse_args()

    content_type = 'json' if args.json else 'html'

    if args.url:
        response = make_request(args.url, content_type)
        print(response)
    elif args.search:
        search(args.search)

if __name__ == "__main__":
    main()