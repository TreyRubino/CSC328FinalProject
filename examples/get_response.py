# Examples. The path will relative to your current working directory
from inc.Model import Response, Content

# This is how the data might look after being received over the network
# `status` and `message` are common JSON fields. They indicate if the interaction
# was successful or not and message provides the details. The rest of the field are custom.
received_data = b'{"status": "success", "message": "Files retrieved", "contents": [{"size": 1024, "name": "file1.txt", "type": "text"}, {"size": 2048, "name": "image1.png", "type": "image"}]}'

try:
    # Decode the received data back into a Python dictionary
    decoded_response = Response.decode(received_data, Response)

    # At this point, `decoded_response` is now a Response object
    # You can access its attributes directly
    print("Decoded Response:")
    print(f"Status: {decoded_response.status}")
    print(f"Message: {decoded_response.message}")
    print("Contents:")
    for content in decoded_response.contents:
        print(f"  - Name: {content.name}, Size: {content.size}, Type: {content.type}")

    # (optional) You can also use the validate method to confirm it aligns with our protocol.
    decoded_response.validate()
    print("\nResponse is valid.")
except ValueError as e:
    print(f"Validation failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
