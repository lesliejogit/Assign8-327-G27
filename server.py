import socket
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz  # For time zone conversion

valid_queries = [
    "What is the average humidity inside my kitchen fridge 1 in the past three hours?",
    "What is the average humidity inside my kitchen fridge 2 in the past three hours?",
    "What is the average water level in my dishwasher in the past three hours?",

]

# Helper function for unit conversion (e.g., converting moisture readings to RH)
def convert_moisture_to_rh(moisture):
    return moisture * 0.5  # Placeholder conversion factor

# Helper function to convert time to PST (Pacific Standard Time)
def convert_to_pst(timestamp):
    timezone = pytz.timezone("US/Pacific")
    local_time = timestamp.astimezone(timezone)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

# Connect to MongoDB (Use the connection string provided by you for MongoDB Atlas)
def connect_to_db():
    try:
        client = MongoClient('mongodb+srv://jezseeca:1234@matcha.seofb.mongodb.net/?retryWrites=true&w=majority&appName=matcha')
        db = client['test']  # Database name, replace as needed
        return db
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Query handler function
from datetime import datetime, timedelta

def process_query(query, db):
    if query == "What is the average humidity inside my kitchen fridge 1 in the past three hours?":
        collection = db['matchatable_virtual']  # Collection name
        three_hours_ago = datetime.now() - timedelta(hours=3)
        
        # Convert datetime to Unix timestamp in seconds
        three_hours_ago_timestamp = int(three_hours_ago.timestamp())  # Convert to Unix timestamp
        
        print("Time threshold (3 hours ago):", three_hours_ago)
        
        # Query the database for data related to Fridge1 (asset_uid or topic)
        cursor = collection.find({
            'topic': 'home/kitchen/fridge',  # Filter by topic for kitchen fridges
            'timestamp': {'$gt': str(three_hours_ago_timestamp)},  # Convert to string for comparison
            'asset_uid': 'q9b-kb8-303-99s'  # Example: Fridge 1 asset UID
        })
        
        # Check if the cursor has any documents by converting the cursor to a list and checking length
        docs_list = list(cursor)
        print(f"Documents found: {len(docs_list)}")  # This will print the number of documents the cursor returns
        
        total_humidity = 0
        count = 0
        
        # Fetch documents and calculate the average humidity
        for doc in docs_list:
            print("Document fetched:", doc)  # Debugging line to check the document content
            
            # Extract Fridge1's humidity value
            humidity = doc.get('payload', {}).get('Fridge1_Humidity')
            if humidity:
                total_humidity += float(humidity)
                count += 1
            else:
                print("No humidity data found in this document.")
        
        # If there are no documents or no humidity data, the average humidity will be 0
        average_humidity = total_humidity / count if count > 0 else 0
        return f"Average humidity inside Fridge1 in the past 3 hours: {average_humidity:.2f}%"

    # Example query for Fridge2's humidity in the past 3 hours
    elif query == "What is the average humidity inside my kitchen fridge 2 in the past three hours?":
        collection = db['matchatable_virtual']  # Collection name
        three_hours_ago = datetime.now() - timedelta(hours=3)
        
        # Query the database for data related to Fridge2 (asset_uid or topic)
        cursor = collection.find({
            'topic': 'home/kitchen/fridge',
            'timestamp': {'$gt': three_hours_ago},
            'asset_uid': 'f40377a7-156a-4a82-8625-f245bfaf0fee'  # Example: Fridge 2 asset UID
        })
        
        # Calculate the average humidity from Fridge2 data
        total_humidity = 0
        count = 0
        for doc in cursor:
            humidity = doc.get('Fridge2_Humidity')  # Extract Fridge2's humidity value
            if humidity:
                total_humidity += float(humidity)
                count += 1
        
        average_humidity = total_humidity / count if count > 0 else 0
        return f"Average humidity inside Fridge2 in the past 3 hours: {average_humidity:.2f}%"

    # Example query for the dishwasher's water level in the past 3 hours
    elif query == "What is the average water level in the dishwasher in the past three hours?":
        collection = db['matchatable_virtual']  # Collection name
        three_hours_ago = datetime.now() - timedelta(hours=3)
        
        # Query the database for data related to the dishwasher (using asset_uid or topic)
        cursor = collection.find({
            'topic': 'home/kitchen/fridge',  # Assuming this topic can cover the dishwasher too
            'timestamp': {'$gt': three_hours_ago},
            'asset_uid': 'rh6-u91-pkx-bcl'  # Example: Dishwasher asset UID
        })
        
        # Calculate the average water level from the dishwasher data
        total_water_level = 0
        count = 0
        for doc in cursor:
            water_level = doc.get('Water Level Sensor')  # Extract water level value for dishwasher
            if water_level:
                total_water_level += float(water_level)
                count += 1
        
        average_water_level = total_water_level / count if count > 0 else 0
        return f"Average water level in the dishwasher in the past 3 hours: {average_water_level:.2f} liters"
    
    # If none of the above queries match, provide a fallback message
    else:
        valid_queries_str = "\n".join(valid_queries)  # Join the list into a readable string
        return f"Sorry, this query cannot be processed. Please try one of the following queries:\n\n{valid_queries_str}"

# Main function to start the server
def main():
    server_port = int(input("Enter the server port number: "))
    
    # Port checker
    if server_port < 1024 or server_port > 65535:
        print("ERROR: Please enter a valid port number.")
        return

    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', server_port))
    server_socket.listen(1)
    
    print(f"Listening on port {server_port}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established with {client_address}")

        # Connect to the MongoDB database
        db = connect_to_db()
        if db is None:
            client_socket.close()
            continue

        while True:
            message = client_socket.recv(4096).decode()
            if not message:
                print(f"Connection closed by {client_address}")
                break

            print("Received message:", message)

            # Process the query and retrieve results
            response = process_query(message, db)

            # Send the result back to the client
            client_socket.sendall(response.encode())

        # Close client socket and database connection
        client_socket.close()

    server_socket.close()

if __name__ == "__main__":
    main()  # Entry point of the program
