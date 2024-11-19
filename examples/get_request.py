# Examples. The path will relative to your current working directory
from inc.Model import Request

# Example of what the user input string might look like
# get file.txt and put it in my current directory
user_input = 'get file.txt .'

try:
    parts = user_input.split()      # Split the whole string into parts
    cmd = parts[0]                  # First part is the command
    remote_path = parts[1]          # Second part is the remote path
    local_path = parts[2]           # Third part is the local path

    # Construct the Request object. Using the custom Request model, pass in the parameters.
    request = Request(
        cmd=cmd,
        remote_path=remote_path,
        local_path=local_path,
    )
    
    # Now the Request has been built the last step is to validate and encode.
    # You can use the request.prepare() method to achieve this. 
    finalRequest = request.prepare()

    # The Request is now ready to be sent.
    # We can take the size of the `finalRequest` variable to send to the client / server
    # first and then send the full request.
except IndexError:
    print("Invalid input format. Usage: <cmd> <remote_path> <local_path> [y/n]")