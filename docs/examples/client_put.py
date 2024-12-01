command = "put example.txt uploaded_example.txt"
args = command.split()

if args[0] == "put":
    # Extract paths
    local_path = args[1]
    remote_path = args[2] if len(args) > 2 else os.path.basename(local_path)

    # Build the Request object
    request = Request(cmd="put", local_path=local_path, remote_path=remote_path)

    # Call the utility's put method
    response = utility.put(conn, request)

    # Handle the server's response
    if response.status == "success":
        print(f"File '{local_path}' uploaded successfully as '{remote_path}'.")
    else:
        print(f"Error: {response.message}")
