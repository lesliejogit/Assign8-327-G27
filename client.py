import socket
import ipaddress

# Valid queries list
valid_queries = [
    "What is the average humidity inside my kitchen fridge 1 in the past three hours?",
    "What is the average humidity inside my kitchen fridge 2 in the past three hours?",
    "What is the average water level in my dishwasher in the past three hours?",
]


def get_server_details():
    # Asks user for IP address
    server_ip = input("Enter the server IP address: ")
    
    # IP address checker
    try:
        ipaddress.ip_address(server_ip)  # Validates IP address format
    except ValueError:
        print("ERROR: Invalid IP address format.")
        return None, None  # Returning None to indicate an IP address error
    
    # Asks user for port number
    server_port = int(input("Enter the server port number: "))
    
    # Port checker -- checks if the port number is valid
    if server_port < 1024 or server_port > 65535:
        print("ERROR: Please enter a valid port number.")
        return None, None  # Returning None to indicate a port number error
    
    return server_ip, server_port

def handle_user_query(message):
    """
    Handles the user query and checks if it matches any of the valid queries.
    """
    if message in valid_queries:
        return True
    else:
        print(f"Sorry, this query cannot be processed. Please try one of the following:")
        for query in valid_queries:
            print(f"- {query}")
        return False

def main():
    while True:
        # Retrieve server details with validation
        server_ip, server_port = get_server_details()
        if server_ip is None or server_port is None:  # Check for validation error
            continue  # Prompt for details again

        # Create TCP socket and connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((server_ip, server_port))  # Connects to the server
                print("Connected to the server.")
            except socket.error:
                print("ERROR: Unable to connect to the server. Please check the IP address and port.")
                continue  # Prompt for details again if connection fails

            while True:
                # Ask for user input message
                message = input("Enter your message (or type 'exit' to quit): ")
                
                if message.lower() == 'exit':
                    break  # if user types 'exit' it exits the loop

                # Check if the message is valid
                if handle_user_query(message):
                    # Send valid message to server
                    client_socket.send(message.encode())  # Sends the message to the server
                    
                    # Receive reply from server
                    reply = client_socket.recv(4096)  # Receives response from server
                    print("Server reply:", reply.decode())  # Displays server reply

if __name__ == "__main__":
    main()  # Entry point of the program
