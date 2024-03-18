import socket

def send_request(url):
    try:
        host = url.split('/')[2]
        path = '/' + '/'.join(url.split('/')[3:])
        port = 80

        # Open a socket to the web server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))

            # Send HTTP GET request
            s.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())

            # Receive response
            response = b""
            while True:
                data = s.recv(1024)
                if not data:
                    break
                response += data

        return response.decode()
    except Exception as e:
        return f"Error: {e}"

def search(term):
    search_url = f"http://www.example.com/?q={term}"
    return send_request(search_url)

def print_help():
    print("go2web -u <URL>         # make an HTTP request to the specified URL and print the response")
    print("go2web -s <search-term> # make an HTTP request to search the term using your favorite search engine and print top 10 results")
    print("go2web -h               # show this help")

def main():
    while True:
        command = input("user> ").strip().split()
        
        
        if not command:
            continue

        if(command[0] == 'go2web'):
            index_u = command.index('-u')
            url = command[index_u + 1]
            
            option = command[1]

            if option == '-h':
                print_help()
            elif option == '-u':
                print(send_request(url))
            elif option == '-s':
                if len(command) < 2:
                    print("Invalid usage. Please provide a search term.")
                    continue
                term = ' '.join(command[1:])
                print(search(term))
            elif option == 'exit':
                break
            else:
                print("Invalid option. Use '-h' for help.")
        else:
            print("Invalit command")

if __name__ == "__main__":
    main()
# go2web -u https://getbootstrap.com/docs/5.0/layout/containers/