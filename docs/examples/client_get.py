command = "get uploaded_example.txt downloaded_example.txt"
args = command.split()

if args[0] == "get":
    # Extract paths
    remote_path = args[1]
    local_path = args[2] if len(args) > 2 else os.path.basename(remote_path)

    # Build the Request object
    request = Request(cmd="get", remote_path=remote_path, local_path=local_path)

    # Call the utility's get method
    response = utility.get(conn, request)

    # Handle the server's response
    if response.status == "success":
        print(f"File '{remote_path}' downloaded successfully to '{local_path}'.")
    else:
        print(f"Error: {response.message}")
