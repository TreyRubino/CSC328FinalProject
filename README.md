# Custom JSON-Driven SFTP Protocol  
### UNIX Documentation  
**Author: Trey Rubino**  

## ID Block
- **Contrubutors**:
  - **Alexa**: Server Implementation
  - **Ian**: Client Implementation
  - **Trey Rubino**: Utility Code, Documentation, Protocol Design, and Implementation

The main contributor's name is the first at top of a given file, with the assisting contributors coming second and third.  

## Contents

1. **Request Class**  
   - [1.1 Attributes and Data Types](#attributes-and-data-types)  
   - [1.2 Examples of Valid Payloads](#examples-of-valid-payloads)  
2. **Response Class**  
   - [2.1 Attributes and Data Types](#attributes-and-data-types-1)  
   - [2.2 Examples of Valid Payloads](#examples-of-valid-payloads-1)  
3. **CustomProtocol Class**  
   - [3.1 Methods and Descriptions](#methods-and-descriptions)  
4. **Utility Class**  
   - [4.1 Methods and Descriptions](#methods-and-descriptions-1)  
5. **Error Handling**  
   - [5.1 Common Error Codes and Explanations](#common-error-codes-and-explanations)  
6. **How to Run**
   -  [6.1 How to Run this Project](#how-to-run) 
7. **Current Status**
   - [7.1 Current Status of the Project](#current-status)
8. **Request Examples**
9. **Response Examples**
10. **References**

## Overview

The **Utility/Library Code** for this custom protocol is designed as an API that utilizes **JSON** as the primary communication format. This documentation provides an in-depth explanation of the **application programming interface (API)**, detailing function calls, common data structures, and examples of valid request and response data. The protocol works by utilizing the encoding and decoding of JSON metadata. When the protocol needs to send file data, we use a acknowledgement to notify the server / client that they are ready to receive the binary data of the requested file. This makes it easy to work with and capable of working with large files and different kinds of formats. This way we can send basic commands using a text based protocol (JSON) for light weight and simple communication.

### Purpose
This protocol empowers developers to focus solely on the **functionality and features** they wish to implement, abstracting away complexities in the protocol's underlying mechanics. The structure remains **transparent and extensible**, allowing customization as needed.

> **Disclaimer**: Developers must provide their own working client and server implementations. This documentation covers only the API, protocol design, and specific commands.

### File / Folder Manifest

The project was been built using standard application folder and file organization. The `src` folder contains the main scripts to run the server and the client. The `inc` folder contains the implementation of the server as well as the client. Within the `inc` folder there are the `Parser`, `Model`, and `Utility` folders. The `Parser` folder contains scripts to parser the command line arguments for the client and server. The `Utility` folder contains a varity of scripts that bring the common funcitonality to the server and client such as commands and send and recv logic. The `Model` folder contains basic data structures representing the Request and Response of our custom protocol. These files will me explored in greater detail below.

## 1. Request Class  

The **Request Class** encapsulates client-side requests. It is a subclass of `CustomProtocol`.

### Attributes and Data Types

| Attribute      | Type              | Description                                                 |
|----------------|-------------------|-------------------------------------------------------------|
| `cmd`          | String            | Command to be executed (e.g., `ls`, `cd`, `get`).           |
| `local_path`   | Optional[String]  | Path on the local machine.                                  |
| `remote_path`  | Optional[String]  | Path on the remote server.                                  |
| `recursive`    | Optional[Boolean] | Indicates if the command applies recursively.               |
| `size`         | Optional[Integer] | File size for upload or download.                           |

### Examples of Valid Payloads
- A request to list directory contents.  
- A request to upload a file with a specified size.  

## 2. Response Class  

The **Response Class** models server responses and inherits from `CustomProtocol`.

### Attributes and Data Types

| Attribute      | Type              | Description                                                 |
|----------------|-------------------|-------------------------------------------------------------|
| `status`       | String            | Response status (e.g., `success`, `error`).                 |
| `message`      | Optional[String]  | A message accompanying the response.                        |
| `contents`     | Optional[List]    | Directory or file entries for the `ls` command.             |
| `code`         | Optional[String]  | Error or status code for troubleshooting.                   |
| `size`         | Optional[Integer] | File size for upload or download.                           |

### Examples of Valid Payloads
- A successful response listing directory contents.  
- An error response for an invalid directory path.  

## 3. CustomProtocol Class  

The **CustomProtocol Class** provides shared functionality for encoding/decoding JSON and handling binary data.

### Methods and Descriptions

| Method                  | Description                                                       |
|-------------------------|-------------------------------------------------------------------|
| `validate()`            | Ensures the object meets required criteria.                      |
| `prepare()`             | Validates and encodes the object into JSON bytes.                |
| `encode()`              | Encodes the object as JSON bytes.                                |
| `decode(data, cls)`     | Decodes JSON bytes into an instance of the specified class.       |
| `attach_binary_data()`  | Attaches binary data to the object.                              |
| `get_binary_data()`     | Retrieves attached binary data.                                  |

## 4. Utility Class  

The **Utility Class** contains helper methods for managing common operations and data exchange between the client and server.

### Methods and Descriptions  

| Method                 | Description                                                       |
|------------------------|-------------------------------------------------------------------|
| `ls(request)`          | Lists directory contents.                                        |
| `cd(request)`          | Changes the current working directory.                           |
| `mkdir(request)`       | Creates a new directory.                                         |
| `get(conn, request)`   | Downloads a file from the server.                                |
| `put(conn, request)`   | Uploads a file to the server.                                    |
| `send_all(conn, obj)`  | Sends JSON and binary data to the specified connection.          |
| `recv_all(conn, obj_type)` | Receives JSON and binary data from the specified connection. |

## 5. Error Handling  

Error handling ensures robust communication by providing clear feedback for errors encountered during operations.

### Common Error Codes and Explanations  

There a two ways to check if a request is successful, either by check the request.status or the request.code. If status is successful and code is None, the request is valid. Anything else means a error.

| Error Code             | Description                                                       |
|------------------------|-------------------------------------------------------------------|
| `ERR_INVALID_DIR`      | The specified directory path is invalid.                         |
| `ERR_DIR_NOT_FOUND`    | The requested directory could not be found.                      |
| `ERR_PERMISSION_DENIED`| Insufficient permissions to access the specified path.           |
| `ERR_DIR_EXISTS`       | The directory already exists.                                    |
| `ERR_GET_CLIENT`       | An error occurred while retrieving a file from the server.       |
| `ERR_PUT_CLIENT`       | An error occurred while uploading a file to the server.          |
| `ERR_CONNECTION_LOST`  | The connection was lost during data transfer.                    |
| `ERR_CD`               | There was an error changing directories.                         |
| `ERR_INVALID_PATH`     | The path request is invalid.                                     |
| `ERR_REMOVE`           | There was an error during  the remove command.                   |

## 6. How to Run

To run this project is quite simple. Make sure you are in the same file as the MAKEFILE. Make the project with the command `make`. This will generate a folder named `build` and from the root directory of this project you can type `./build/fileserver -d ./ -p 12345` to run the server and `./build/fileclient -h localhost -p 12345` to run the provided client.

## 7. Current Status

Currently all required commands should be completely functional, with the exception of -r on `get` and `put` does not work. You can only send and receive a single file. There are also a few additional commands such as `rm`, `cat`, and `clear`. The server provided also reflects additional functionality. The server is capable of displaying a formatted view into all connected clients displaying and dynamically updating connection length, last command, and the client current working directory. All local and remote commands work the same way, just prefix the command with an `l` to specify that you want to execute the command locally.

## 8. Request Examples
```json
{
   "cmd": "put",
   "options": []
   "remote_path": "example.txt",
   "local_path": "example/",
   "size": 0
}
```

```json
{
   "cmd": "get",
   "options": []
   "remote_path": "example.txt",
   "local_path": "example/",
   "size": 0
}
```

```json
{
   "cmd": "cd",
   "options": [],
   "remote_path": "example/",
   "local_path": None
   "size": 0
}
```

```json
{
   "cmd": "ls",
   "options": [-l]
   "remote_path": "example/",
   "local_path": None,
   "size": 0
}
```

```json
{
   "cmd": "mkdir",
   "options": [],
   "remote_path": "example/",
   "local_path": None,
   "size": 0
}
```

```json
{
   "cmd": "mkdir",
   "options": [-r],
   "remote_path": "example/example/",
   "local_path": None,
   "size": 0
}
```

```json
{
   "cmd": "clear",
   "options": [],
   "remote_path": None,
   "local_path": None,
   "size": 0
}
```

```json
{
   "cmd": "cat",
   "options": [],
   "remote_path": "example.txt",
   "local_path": None,
   "size": 0
}
```

```json
{
   "cmd": "help",
   "options": [],
   "remote_path": None,
   "local_path": None,
   "size": 0
}
```

```json
{
   "cmd": "rm",
   "options": [],
   "remote_path": "example.txt",
   "local_path": None,
   "size": 0
}
```

```json
{
   "cmd": "rm",
   "options": [-r],
   "remote_path": "example/",
   "local_path": None,
   "size": 0
}
```

```json
{
   "cmd": "pwd",
   "options": [],
   "remote_path": None,
   "local_path": None,
   "size": 0
}
```

## 9. Response Examples

```json
{
    "status": "success",
    "message": "Directory listing retrieved successfully.",
    "contents": [
        {
            "mode": "-rw-r--r--",
            "nlink": 1,
            "user": "trey",
            "group": "users",
            "size": 1024,
            "mtime": "2023-12-12 10:15:30",
            "name": "file1.txt"
        },
        {
            "mode": "drwxr-xr-x",
            "nlink": 2,
            "user": "trey",
            "group": "users",
            "size": 4096,
            "mtime": "2023-12-11 14:22:10",
            "name": "subdir"
        }
    ],
    "code": None,
    "size": 0
}
```

```json
{
    "status": "success",
    "message": "Changed directory to /example.",
    "contents": [],
    "code": null,
    "size": 0
}
```

```json
{
    "status": "error",
    "message": "The specified directory does not exist.",
    "contents": [],
    "code": "ERR_DIR_NOT_FOUND",
    "size": 0
}
```

## 10. References

### Python Official Documentation
1. **Python Documentation Home**  
   [https://docs.python.org/3/](https://docs.python.org/3/)

2. **Python `os` Module Documentation**  
   [https://docs.python.org/3/library/os.html](https://docs.python.org/3/library/os.html)

3. **Python `sys` Module Documentation**  
   [https://docs.python.org/3/library/sys.html](https://docs.python.org/3/library/sys.html)

4. **Python `dataclasses` Module Documentation**  
   [https://docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html)

5. **Python `json` Module Documentation**  
   [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)

6. **Python `typing` Module Documentation**  
   [https://docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html)


### Wiki Pages on Text Protocols and Communication
1. **Text-Based Protocols - Wikipedia**  
   [https://en.wikipedia.org/wiki/Text-based_protocol](https://en.wikipedia.org/wiki/Text-based_protocol)

2. **Client–Server Model - Wikipedia**  
   [https://en.wikipedia.org/wiki/Client%E2%80%93server_model](https://en.wikipedia.org/wiki/Client%E2%80%93server_model)

3. **Comparison of File Transfer Protocols - Wikipedia**  
   [https://en.wikipedia.org/wiki/Comparison_of_file_transfer_protocols](https://en.wikipedia.org/wiki/Comparison_of_file_transfer_protocols)


### General Networking and Communication
1. **Sockets Programming HOWTO - Python Docs**  
   [https://docs.python.org/3/howto/sockets.html](https://docs.python.org/3/howto/sockets.html)

2. **Networking and Interprocess Communication - Python Docs**  
   [https://docs.python.org/3/library/ipc.html](https://docs.python.org/3/library/ipc.html)




