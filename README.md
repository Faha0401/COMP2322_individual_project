# COMP2322_individual_project
This is a project for COMP2322 COMPUTER NETWORKING

The system handles multiple simultaneous client requests through threading, parses HTTP requests (GET/HEAD), and manages data transfer by correctly formatting headers and status codes (200, 304, 403, 404). To optimize performance and resource usage, the server implements HTTP caching via If-Modified-Since, persistent connections (keep-alive), and an efficient file I/O logging system. 
The log file displayed different types of HTTP requests that the server could handle