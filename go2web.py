import sys
import socket
import ssl
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json 
import hashlib

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
                        parsed_response = #parse the html
                        return parsed_response
                    # Check if content type is JSON
                    elif 'application/json' in content_type:
                        # Parse JSON data
                        json_data = json.loads(headers_and_body)
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

def main():
    args = sys.argv[1:]
    print(args)

    if not args:
        print("Follow the help conditions !")
        sys.exit()

    elif '-h' in args:
        print("go2web -u <URL>         # make an HTTP request to the specified URL and print the response")
        print("go2web -s <search-term> # make an HTTP request to search the term using your favorite search engine and print top 10 results")
        print("go2web -h               # show this help")

if __name__ == "__main__":
    main()