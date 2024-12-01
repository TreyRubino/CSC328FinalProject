# Receive the Request
request = utility.recv_all(conn, Request)

if request.cmd == "ls":
    # Process the `ls` command
    response = utility.ls(request)

    # Send the Response back to the client
    utility.send_all(conn, response)
