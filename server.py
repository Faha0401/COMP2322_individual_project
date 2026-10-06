# Implements a simple HTTP Server
import socket
import threading
from email.utils import parsedate_to_datetime, formatdate
import os

# Define socket host and port
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000

def request(client_socket, client_address):  
    while True:
        try:
            # Parse the cmd into fields 
            request = client_socket.recv(1024).decode()
            if not request:
                break
            headers = request.split("\\r\\n")
            fields = headers[0].split()
            Connection = "Connection: close\r\n"
            keep_alive = False
            
            curtime = formatdate(timeval=None, localtime=False, usegmt=True)

            # Find the string If-Modified-Since: and take the string after the : as the date
            client_date = None
            for line in headers[1:]: 
                if line.startswith("If-Modified-Since:"):
                    client_date = line.split(":", 1)[1].strip()
                    break
                
            if len(fields) > 2:
                request_type = fields[0]
                filename = fields[1]
                
                if "Connection: keep-alive" in request:
                    Connection = "Connection: keep-alive\r\n"
                    keep_alive = True
                
                if request_type == 'GET' or request_type == 'HEAD':
                    # If no file was specified
                    if filename == '/':
                        filename = '/index.html'
                    
                    # Open the file
                    try:                  
                        fin = open('file' + filename, 'rb')
                        content = fin.read()
                        fin.close()
                        
                        response = 'HTTP/1.1 200 OK\r\n' + "Date: " + curtime + "\r\n" + Connection 
                
                        # Get the last modified time of the file and format it
                        last_modified = os.path.getmtime("file" + filename)
                        last_modified_date = formatdate(last_modified, usegmt=True)
                        
                        is_modified = True
                        # Handling if modified since
                        if "If-Modified-Since" in request:
                            # Compare the date provided by client and the file modified date
                            if parsedate_to_datetime(client_date).timestamp() >= last_modified:
                                is_modified = False
                                response = 'HTTP/1.1 304 Not Modified\r\n' + "Date: " + curtime + "\r\n" + Connection + "Last-Modified: " + formatdate(last_modified, usegmt=True) + "\r\n\r\n"
                                logger(client_address, curtime, filename, "304 Not Modified")
                                
                        if is_modified:
                            # Only append the last-modified when the file is modified
                            response = response + "Last-Modified: " + last_modified_date + "\r\n"
                            if filename.endswith('.jpg'):
                                response += "Content-Type: image/jpeg\r\n"
                            elif filename.endswith('.txt') or filename.endswith('.html'):
                                response += "Content-Type: text/html\r\n"
                    
                        # Handling the GET or HEAD request
                        if request_type == 'GET' and is_modified:
                            response = response.encode() + f"Content-Length: {len(content)}\r\n\r\n".encode() + content 
                        elif is_modified:
                            response = response + f"Content-Length: {len(content)}\r\n\r\n" 
                            response = response.encode()
                        else:
                            # Handling the HEAD request and does not append the content as 
                            response = response.encode()
                        logger(client_address, curtime, filename, "200 OK")
                    
                    # Handling if file is not found
                    except FileNotFoundError:
                        response = 'HTTP/1.1 404 Not Found\r\n' + "Date: " +  curtime + "\r\n" + Connection + "\r\nFile Not Found"
                        logger(client_address, curtime, filename, "404 Not Found")
                        response = response.encode() 
                    # Handling if the file is not allow to be access 
                    except PermissionError:
                        response = 'HTTP/1.1 403 Forbidden\r\n' + "Date: " + curtime + "\r\n" + Connection + "\r\n"
                        logger(client_address, curtime, filename, "403 Forbidden")
                        response = response.encode() 
                else:
                    # Handling other request that is not allowed
                    response = 'HTTP/1.1 400 Bad Request\r\n' + "Date: " + curtime + "\r\n" + Connection + "\r\n"
                    logger(client_address, curtime, filename, "400 Bad Request")
                    response = response.encode() 
            else:
                # Directly sends bad request if the field is not enough
                response = 'HTTP/1.1 400 Bad Request\r\n' + "Date: " + curtime + "\r\n" + Connection + "\r\n"
                logger(client_address, curtime, filename, "400 Bad Request")
                response = response.encode()     
            client_socket.sendall(response)
            print(f"Sending response to client {client_address}...")
            
            # End the client thread if it's not a persistent connection
            if not keep_alive:
                break
            
        except Exception as e:
            print(f"Unexpected exception: {e}")
    print(f"Closing connetion with client {client_address}")
    client_socket.close()
    
def server():
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(10)
    
    # Clear the log file 
    # open("log.txt", "w").close
    
    print('Listening on port %s ...' % SERVER_PORT)

    while True:
        # Wait for client connections
        client_connection, client_address = server_socket.accept()
        print(f"Connected with client {client_address} ")
        # Creating a new client thread
        thread = threading.Thread(target=request, args=(client_connection, client_address, ))
        thread.start()
        
        
def logger(client_host_ip, access_time, file_name, response_type):
    log = open("log.txt", "a")
    log.write(f"Client IP address: {client_host_ip}, Access time: {access_time}, Access file: {file_name}, Response type: {response_type}\r\n")
server()