#import required libraries
import sys
import socket
from urllib.parse import urlparse
from pathlib import Path

CACHE_DIRECTORY = 'cache'  

def parse_request_url(request):
    lines = request.split('\r\n')   
    method, url, version = lines[0].split(' ')  #Splitting the url in 3 parts method, url and version
    parsed_url = urlparse(url)
    host = parsed_url.netloc   #zhiju.me
    path = parsed_url.path     #/networks/valid.html
    port = parsed_url.port or 80
    return method, host, port, path, version

def call_web_server(method, host, port, path, version):
    try:
        # Create a socket connection to the remote server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((host, port))

        # Send the modified request to the remote server
        server_socket.send(f'{method} {path} {version}\r\nHost: {host}\r\nConnection: close\r\n\r\n'.encode())

        # Receive the response from the remote server
        response = b''
        while True:
            data = server_socket.recv(1024)
            if not data:
                break
            response += data      #appending data to response, response contains content along with some extra headers


        # Close the connection to the remote server
        server_socket.close()
        
        return response
    except Exception as e:
        print(f'Error connecting to server: {e}')
        return b'HTTP/1.1 500 Internal Error\r\n\r\n'


#function for handling client's request
def handle_request(Clientsocket):  
    # Receive request from the client
    request = Clientsocket.recv(1024).decode()

    print("Received a message from this client", request)

    # Divide the request into parts
    method, host, port, path, version = parse_request_url(request)
 
    #Extract the cache path from url
    cache_path = cache_directory /host/ Path(path[1:])   #creates cache/zhiju.me/networks/valid.html recursive folders

    # Check if the requested file is in the cache
    if cache_path.is_file():
        print("Yeah! The requested file is in the cache and is about to be sent to the client")
        # Get the file from the cache
        with open(cache_path, 'rb') as file:
            response = file.read()
            response += b'\r\n'
            http_ok = bytes(version,'utf-8')+ b' 200 ok\r\n'
            Clientsocket.send(http_ok)
            cache_hit = b'Cache-Hit: 1\r\n'
            Clientsocket.send(cache_hit)
    else:
        print("Oops! No cache hit! Requesting origin server for the file...")
        print (f'Sending the following msg from the proxy to server:', request,'\n host:',host, 'Connection close')
        # Fetch the file from the server
        response = call_web_server(method, host, port, path, version)
        cache_hit = b'Cache-Hit: 0\r\n'
        Clientsocket.send(cache_hit)

        #checks if sub folder is present or not. if not, creates one
        sub_directory = Path(cache_path).parent
        sub_directory.mkdir(parents=True,exist_ok=True)
        
        # Cache the file if the response is successful
        if response.startswith(b'HTTP/1.1 200'):
            print(f'Response received from server , and status code is 200! Write to cache to save time next time... ')
            headers,response = response.split(b'\r\n\r\n',1) #separates headers and response body
            http_ok = headers.split(b"\r\n")[0]+b"\r\n"   #For displaying HTTP 1.1/200 Ok 
            Clientsocket.send(http_ok)
            with open(cache_path, 'wb') as file:
                file.write(response)  
            response += b'\r\n'
        elif response.startswith(b'HTTP/1.1 404'): #response for 404 page not found
            print(f'Response received from server , and status code is not 200! No cache writing... ')
            headers,response = response.split(b'\r\n\r\n',1) #separates headers and response body
            http_ok = headers.split(b"\r\n")[0]+b"\r\n"  
            Clientsocket.send(http_ok)
            response = b'404 NOT FOUND'
            response += b'\r\n'
        else:  #response for internal server error
            print(f'Response received from server , and status code is not 200! No cache writing... ')
            headers,response = response.split(b'\r\n\r\n',1) #separates headers and response body
            http_ok = headers.split(b"\r\n")[0]+b"\r\n"  
            Clientsocket.send(http_ok)
            response = b'UNSUPPORTED ERROR'
            response += b'\r\n'

    print("Now responding the client...")



    # Send the response to the client
    Clientsocket.send(response)
    print("All done! Closing socket...")

    # Close the connection to the client
    Clientsocket.close()


def create_proxy_server(port):
    # Create a socket for the proxy server
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      
    proxy_socket.bind(('localhost', port))
    proxy_socket.listen(1)
    print('*************** Ready to serve ***************')

    # Accept incoming client connections
    while True:
        #clients socket and client address
        Clientsocket, address = proxy_socket.accept()   
        print(f'Received a client connection from:  {address}')

        # Handle the client request in a separate thread
        handle_request(Clientsocket)

if __name__ == '__main__':
    #checks if in argument port number is specified
    if len(sys.argv) != 2:    
        print('Port number is not specified.')
        sys.exit()             
    port = int(sys.argv[1])
    server_port = port + (4194679) % 100    
     # Create the cache directory if it doesn't exist
    cache_directory = Path(CACHE_DIRECTORY)
    cache_directory.mkdir(parents=True, exist_ok=True)     
    create_proxy_server(port)