command = "ls /remote/directory"
args = command.split()

if args[0] == "ls":
    # Extract the remote path
    remote_path = args[1] if len(args) > 1 else None

    # Build the Request object
    request = Request(cmd="ls", remote_path=remote_path)

    # Send the Request and receive the Response
    utility.send_all(conn, request)
    response = utility.recv_all(conn, Response)

    # Handle the server's response
    if response.status == "success":
        print("Directory listing:")
        for entry in response.contents:
            print(f"{entry.type}: {entry.name} ({entry.size} bytes)")
    else:
        print(f"Error: {response.message}")
