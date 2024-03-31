import sys
import socket

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