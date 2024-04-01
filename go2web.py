import sys
import socket
import ssl
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json 
import hashlib
import requests
from tinydb import TinyDB, Query


def parse_HTML(response):
    # Parse the HTML response using BeautifulSoup
    soup = BeautifulSoup(response, 'html.parser')
    # Find all elements of interest: headers (h1-h6) and paragraphs (p)
    elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
    
    # Initialize a list to store parsed data
    data = []

    # Iterate over found elements
    for element in elements:
        # If the element is a header
        if element.name.startswith('h'):
            # Append header text with respective level indicator to the data list
            data.append(f"{element.name.upper()}: {element.get_text()}")
        # If the element is a paragraph
        elif element.name == 'p':
            # Append paragraph text with 'P' indicator to the data list
            data.append(f"P: {element.get_text()}")

    # Find all anchor tags with href attribute (links)
    links = soup.find_all('a', href=True)
    # Extract href attribute value for links starting with 'http'
    links_href = [link['href'] for link in links if link['href'].startswith('http')]
    # Add a separator and links to the data list
    data.append("-- Links --")
    data += links_href

    # Return the parsed data
    return data

def handle_TCP(url):
    try:
        # Parse the URL to extract host and path
        parsed_url = urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path if parsed_url.path else '/'

        # Create a default SSL context
        context = ssl.create_default_context()

        # Establish a TCP connection to the host
        with socket.create_connection((host, 443)) as sock:
            # Wrap the socket with SSL
            with context.wrap_socket(sock, server_hostname=host) as s:
                # Send HTTP GET request to the server
                s.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
                response = b''  # Initialize an empty response buffer
                # Receive response data in chunks
                while True:
                    data = s.recv(4096)
                    if not data:  # Break the loop if no more data is received
                        break
                    response += data  # Append received data to the response buffer

        # Decode and return the response
        return response.decode()  

    except Exception as e:
        # Catch and return any exceptions as a string
        return str(e)
    

def handle_HTTP(url):
    try:
        if is_cached(url):
            # If the URL is cached, print a message indicating that a cached response is being retrieved
            print("Retrieving cached response for:", url)
            # Retrieve and return the cached response
            return retrieve_cached_response(url)
                
        # Make a TCP request to the specified URL
        response = handle_TCP(url)
        
        # Check if the response contains the header and body separator '\r\n\r\n'
        if '\r\n\r\n' in response:
            # Split the response into status line and headers/body
            status_line, headers_and_body = response.split('\r\n\r\n', 1)
            # Extract status code from the status line
            status_code = int(status_line.split()[1])
            # Parse headers into a dictionary
            headers = dict(header.split(": ", 1) for header in status_line.split("\r\n")[1:])
            # Extract Content-Type header from headers
            content_type = headers.get('Content-Type')

            # Check if the status code is 200 (OK)
            if status_code == 200:
                if content_type:
                    # Check if content type is HTML
                    if 'text/html' in content_type:
                        # Call function to parse HTML response
                        parsed_response = parse_HTML(headers_and_body)
                        cache_response(url, parsed_response)  # Cache HTML responses
                        return parsed_response
                    # Check if content type is JSON
                    elif 'application/json' in content_type:
                        # Parse JSON data
                        json_data = json.loads(headers_and_body)
                        cache_response(url, json_data)  # Cache JSON responses
                        return json_data
                    else:
                        # Unsupported content type
                        return [f"Content type not supported: {content_type}"]
                else:
                    #Content-Type header not found
                    return [f"Header of Content-Type not found"]
            else:
                #Status code is not 200
                return [f"Status code{status_code}"]
        else:
            #Response format is invalid
            return [f"The response format for HTTP in not valid"]
    except Exception as e:
        # Catch and return any exceptions as a string
        return [str(e)]


# Define the cache file name
cache_file = "cache_data.json"
# Initialize TinyDB with the cache file
db = TinyDB(cache_file)

# Function to hash a URL using MD5
def hash_url(url):
    return hashlib.md5(url.encode()).hexdigest()

# Function to cache a response with its corresponding hashed URL
def cache_response(url, response):
    db.insert({'url': hash_url(url), 'response': response})

# Function to check if a URL is cached
def is_cached(url):
    return db.contains(Query().url == hash_url(url))

# Function to retrieve cached response for a URL
def retrieve_cached_response(url):
    result = db.get(Query().url == hash_url(url))
    return result['response']

def handle_SEARCH(term):
    search_url = f"https://www.google.md/search?q={term}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract top 10 results and print them
    for i, result in enumerate(soup.find_all('a')[16:26], start=1):
        print(f"{i}. {result.text} - {result['href']}")
        

def main():
    args = sys.argv[1:]

    if not args:
        print("Follow the help conditions !")
        sys.exit()

    if '-h' in args:
        print("go2web -u <URL>         # make an HTTP request to the specified URL and print the response")
        print("go2web -s <search-term> # make an HTTP request to search the term using your favorite search engine and print top 10 results")
        print("go2web -h               # show this help")


    elif '-u' in args:
        url_index = args.index('-u') + 1
        if url_index < len(args):
            url = args[url_index]
            response = handle_HTTP(url)
            print("HTML data", url, ":")
            for info in response:
                print(info)
        else:
            print("Need to provide the url")
            sys.exit()

    elif '-s' in args:
        search_index = args.index('-s') + 1
        if search_index < len(args):
            term = ' '.join(args[search_index:])
            print("Search results for", term, ":")
            handle_SEARCH(term)
        else:
            print("Error: No search term provided after -s")
            sys.exit()

if __name__ == "__main__":
    main()