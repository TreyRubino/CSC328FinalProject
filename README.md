# Fall 2024 CSC328 Final Project Design Document (SFTP REPL)
### Trey Rubino, Ian Bull, and Alexa Fisher

## **Project Overview**
This project implements a custom protocol for secure file transfer between a client and server. It includes modular design, collaborative development, and rigorous testing. The design meets all specified requirements and lays out the implementation roadmap for the client, server, and shared library.

## **1. Project Members and Responsibilities**
- **Trey Rubino (Project Manager)**:
  - Library/utility code implementation.
  - Readme documentation.
- **Ian Bull**:
  - Client implementation.
- **Alexa Fisher**:
  - Server implementation.

## **2. Communication Plan**
- **Communication Method**: Text messages (team members have shared contact information).
- **Team Meetings**: Conducted via Zoom as needed, with meeting links shared by the Project Manager.

## **3. Programming Language**
- **Language**: Python is used for the client, server, and shared library due to its:
  - Easy-to-read syntax.
  - Built-in support for JSON and binary data handling.
  - Flexibility and modularity for protocol design.

## **4. Project Files**
https://github.com/TreyRubino/CSC328FinalProject

## **5. Library Functionality**
The shared library provides common functionalities required by both the client and server, ensuring modularity and reusability:
- **Session Class**:
  - Tracks connected clients’ information (e.g., timestamps, IP addresses, connection durations).
  - Facilitates parent-child communication using pipes for data sharing.
- **Utility Classes**:
  - **Utility**: Common functionality (e.g., file operations, checksums).
  - **ClientUtility**: Client-specific utility functions (e.g., command handling).
  - **ServerUtility**: Server-specific utility functions (e.g., file system interaction).
- **Model Classes**:
  - **Request**: Encapsulates JSON-based client requests, with properties like:
    - `cmd`, `remote_path`, `local_path`, `size`, `recursive`.
  - **Response**: Represents server responses with properties like:
    - `status`, `message`, `contents[]`.


## **6. Application Protocol**
### **Overview**
Our custom SFTP protocol facilitates secure file transfer:
- **Metadata** (commands, file names, sizes): Transmitted as JSON for readability.
- **File Data**: Sent in binary chunks for efficiency.

### **Process Flow**
1. JSON metadata initiates the transfer.
2. File data is transmitted as binary chunks.
3. JSON status message signals completion.

### **Design Enhancements/Ideas**
- Append a `\n` character to signify the end of a message for simple commands.
- Include a `size` field in the JSON payload for additional clarity when sending files.
- Custom session among the threads for "global" visibility to all clients connected and their information (IP, FD, connection length, last command).

### **Security**
- Implement constraints to prevent clients from unrestricted navigation of server files.
- Limit file system access to permitted directories.
- Encrypt the session between a given client and the server


## **7. Client and Server Design**

### **Client Workflow**
1. Connect to the server.
2. Receive `"BEGIN"` from the server.
3. Start REPL interface for sending commands and receiving responses.
4. Send commands like `get`, `put`, or `ls`.
5. Exit gracefully by closing sockets and receiving `"END"` from the server.

### **Server Workflow**
1. Parse command-line arguments for port and directory.
2. Create a server socket and listen for connections.
3. Accept connections and fork a child process to handle each client.
4. Respond to commands such as `get`, `put`, or `ls`.
5. Send `"BEGIN"` and `"END"` messages to clients for session control.
6. Handle errors gracefully and allow for a clean shutdown using `ctrl+C`.


## **8. Example Requests and Responses**

### **Client Requests**
- **get**:
  ```json
  {
      "cmd": "get",
      "remote_path": "example.txt",
      "local_path": ".",
      "recursive": false
  }\n
  ```

- **ls**:
  ```json
  {
      "cmd": "ls",
      "remote_path": "documents",
      "local_path": "",
      "recursive": false,
      "size": 0
  }\n
  ```

- **mkdir**:
  ```json
  {
      "cmd": "ls",
      "remote_path": "directory",
      "local_path": "",
      "recursive": false,
      "size": 0
  }\n
  ```

  - **pwd**:
  ```json
  {
      "cmd": "pwd",
      "remote_path": ".",
      "local_path": "",
      "recursive": false,
      "size": 0
  }\n
  ```

  - **cd**:
  ```json
  {
      "cmd": "cd",
      "remote_path": "newDirectory",
      "local_path": "",
      "recursive": false,
      "size": 0
  }
  ```

  - **mkdir**:
  ```json
  {
      "cmd": "mkdir",
      "remote_path": "directory",
      "local_path": "",
      "recursive": false,
      "size": 0
  }
  ```

- **put**:
  ```json
  {
    "cmd": "put",
    "local_path": "example.txt",
    "remote_path": "uploaded_example.txt",
    "recursive": false,
    "size": 12345,
  }\n
  ```

### **Server Responses**
- **get**:
  ```json
  {
    "status": "BEGIN",
    "name": "file.txt",
    "size": 12345,
  }
  ```

- **ls**:
  ```json
  {
    "status": "success",
    "contents": [
        {
            "type": "file",
            "name": "example.txt",
            "size": 12345
        },
        {
            "type": "directory",
            "name": "documents"
        }
    ]
  }\n
  ```



### **File Transfer Process**
  ```json
  {
    "status": "BEGIN",
    "name": "file.txt",
    "size": 12345
  }\n
  ```
  
  Send Big E. binary bits between these two indicators.

  ```json
  {
    "status": "END",
  }\n
  ```

## **9. Testing Plan**

### **Pass Scenarios**
1. **Invalid Command**:  
   - **Input**: `Getls`  
   - **Expected Output**:  
     `"That command doesn’t exist. Try again."`

2. **Invalid Directory**:  
   - **Input**: `cp ../ancestor.txt .`  
   - **Expected Output**:  
     `"Ancestor directory cannot be reached."`

3. **Exit Command**:  
   - **Input**: `exit`  
   - **Expected Output**:  
     Successfully exits the REPL interface.

4. **Recursive Copy (`-R` flag)**:  
   - **Input**: Recursive copy command with `-R` flag.  
   - **Expected Output**:  
     All directories copied recursively.

5. **Kill Command**:  
   - **Input**: Kill command issued.  
   - **Expected Output**:  
     Server shuts down in 10 seconds and notifies connected clients.

6. **Zombie Process Check**:  
   - **Input**: General process monitoring after session termination.  
   - **Expected Output**:  
     No zombie processes remain.

### **Fail Scenarios**
1. **Missing Argument**:  
   - **Input**: `./client -p 12345` (missing `-h`)  
   - **Expected Output**:  
     Program detects missing argument and outputs usage error.

## **10. Conclusion**
The hybrid approach of combining text-based JSON for commands with binary data for file transfers ensures:

- Simplicity: Easy debugging and implementation for smaller requests.
- Efficiency: Optimal performance for large payloads using raw binary.
- Security: Safeguards to restrict file access and encrypt communication.

## **11. References**
- https://docs.python.org/3/library/json.html#
- https://en.wikipedia.org/wiki/Communication_protocol#Text-based
- https://en.wikipedia.org/wiki/JSON
- https://www.markdownguide.org/cheat-sheet/
