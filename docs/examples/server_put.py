# Receive the Request
request = utility.recv_all(conn, Request)

if request.cmd == "put":
    # Process the `put` command
    response = utility.put(conn, request)

    # Send the Response back to the client
    utility.send_all(conn, response)
