import json
import time
import serial


# Serial handler class defining the sending and recieving the JSON command packages
class SerialHandler:

    # Initializer initializing the serial connection and performing the handshake
    def __init__(self, com_port, BAUD_RATE=9600, TIMEOUT=2):
        self.com_port = com_port
        self.BAUD_RATE = BAUD_RATE
        self.TIMEOUT = TIMEOUT

        # Start serial connection
        print(f"Connecting to {com_port}...")
        self.ser = serial.Serial(com_port, baudrate=BAUD_RATE, timeout=TIMEOUT)
        time.sleep(2)   # Wait for arduino to reset

        # Perform handshake
        if not self.handshake():
            raise ConnectionError("Failed to handshake with device.")

        # Handshake finished
        print(f"Connected to COM: {com_port}.")


    # Method to perform the handshake
    def handshake(self, retries=3, delay=1):
        for attempt in range(retries):

            # Send handshake JSON package
            handshake_msg = json.dumps({"handshake" : True}) + '\n'
            print("Sending handshake...")
            self.ser.write(handshake_msg.encode('utf-8'))
            time.sleep(0.1)

            # Listen for response
            start_time = time.time()
            while time.time() - start_time < self.TIMEOUT:
                # Read line if available
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8').strip()
                    # Try to deserialize
                    try:
                        # Print response
                        response = json.loads(line)
                        print(json.dumps(response, indent=4, sort_keys=True))

                        # Check if handshake worked
                        if response.get("handshake_ack") == True:
                                print("Handshake successful!")
                                return True
                    # Throw exception when JSON is invalid
                    except json.JSONDecodeError:
                        pass

                # Wait to try again
                time.sleep(0.1)
                print(f"Handshake attempt {attempt+1} failed, retrying...")
                time.sleep(delay)

            # Exit if failed
            print("Handshake failed after retries.")
            return False


    # Method to send a JSON package
    def exchange_package(self, package):
        msg = json.dumps(package) + '\n'
        print(f"Sending package to [{package["dev_id"]}]")

        # Sending package
        self.ser.write(msg.encode('utf-8'))
        time.sleep(0.1)

        # Get response
        return self._read_response()


    # Method to read the response package
    def _read_response(self):
        # Start timer
        start_time = time.time()
        # Read serial bus until timeout
        while time.time() - start_time < self.TIMEOUT:
            # If bus is filled read
            if self.ser.in_waiting:
                line = self.ser.readline().decode('utf-8').strip()
                # If line read
                if line:
                    try:
                        response = json.loads(line)
                        print(f"[{response["dev_id"]}]", json.dumps(response, indent=4, sort_keys=True))
                        return response

                    # Throw exception if parsing failed
                    except Exception as e:
                        print(f"[Error] Failed to parse response: {e}")
                    return
            time.sleep(0.1)
        print(f"[Warning] No response recieved from COM {self.com_port}.")


    # Method to close the serial connection
    def close(self):
        # Check if there is a serial connection to close
        if self.ser and self.ser.is_open:
            # Close connection
            print(f"Closing connection to COM {self.com_port}.")
            self.ser.close()


    # Destructor closing the serial connection
    def __del__(self):
        self.close()


    # Enables as with usage
    def __enter__(self):
        return self


    # Handles cleanup after as with
    def __exit__(self, exc_type, exc_val, axc_tb):
        return self.close()
