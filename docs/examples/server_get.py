# Receive the Request
request = utility.recv_all(conn, Request)

if request.cmd == "get":
    # Process the `get` command
    response = utility.get(conn, request)

    # Send the Response back to the client
    utility.send_all(conn, response)
