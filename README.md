# Custom JSON-Driven SFTP Protocol  
### UNIX Documentation  
**Author: Trey Rubino**  


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


## Overview

The **Utility/Library Code** for this custom protocol is designed as an API that utilizes **JSON** as the primary communication format. This documentation provides an in-depth explanation of the **application programming interface (API)**, detailing function calls, common data structures, and examples of valid request and response data.

### Purpose
This protocol empowers developers to focus solely on the **functionality and features** they wish to implement, abstracting away complexities in the protocol's underlying mechanics. The structure remains **transparent and extensible**, allowing customization as needed.

> **Disclaimer**: Developers must provide their own working client and server implementations. This documentation covers only the API, protocol design, and specific commands.


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

| Error Code             | Description                                                       |
|------------------------|-------------------------------------------------------------------|
| `ERR_INVALID_DIR`      | The specified directory path is invalid.                         |
| `ERR_DIR_NOT_FOUND`    | The requested directory could not be found.                      |
| `ERR_PERMISSION_DENIED`| Insufficient permissions to access the specified path.           |
| `ERR_DIR_EXISTS`       | The directory already exists.                                    |
| `ERR_GET_CLIENT`       | An error occurred while retrieving a file from the server.       |
| `ERR_PUT_CLIENT`       | An error occurred while uploading a file to the server.          |
| `ERR_CONNECTION_LOST`  | The connection was lost during data transfer.                    |


