import socket
import subprocess
import re
import os

# UDP Server configuration
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 5005     # Choose an available port

def get_cpu_temperature():
    """Retrieves the Raspberry Pi CPU temperature."""
    try:
        # Execute the vcgencmd command to get the temperature
        # "/opt/vc/bin/vcgencmd" may vary slightly based on RPi OS version.
        # In some cases, "/usr/bin/vcgencmd" might also work.
        # You can test both to see which works for your setup.
        command_output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        # Extract the temperature value using a regular expression
        match = re.search(r'-?\d+\.?\d*', command_output)
        if match:
            return float(match.group())
        else:
            return None
    except Exception as e:
        print(f"Error getting CPU temperature: {e}")
        return None

def reboot_system():
    """Reboots the Raspberry Pi using sudo reboot command."""
    try:
        print("Executing reboot command...")
        subprocess.run(["sudo", "reboot"], check=True)
        return True
    except Exception as e:
        print(f"Error executing reboot command: {e}")
        return False

def main():
    # Create a UDP socket.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the specified IP and port.
    sock.bind((UDP_IP, UDP_PORT))

    print(f"UDP server listening on {UDP_IP}:{UDP_PORT}")

    while True:
        # Receive data and the sender's address.
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes.
        received_message = data.decode().strip()

        print(f"Received message: '{received_message}' from {addr}")

        if received_message == "GET_TEMP":
            temperature = get_cpu_temperature()
            if temperature is not None:
                response_message = f"{temperature}°C"
                print(f"Sending response: '{response_message}' to {addr}")
                # Send the temperature back to the client.
                sock.sendto(response_message.encode(), addr)
            else:
                response_message = "Error: Could not retrieve temperature."
                print(f"Sending error response: '{response_message}' to {addr}")
                sock.sendto(response_message.encode(), addr)
        
        elif received_message == "GET_BOOT":
            print(f"Reboot command received from {addr}")
            response_message = "Rebooting system..."
            print(f"Sending response: '{response_message}' to {addr}")
            # Send acknowledgment before rebooting
            sock.sendto(response_message.encode(), addr)
            
            # Execute reboot command
            reboot_success = reboot_system()
            if not reboot_success:
                error_message = "Error: Failed to execute reboot command."
                print(f"Sending error response: '{error_message}' to {addr}")
                sock.sendto(error_message.encode(), addr)

if __name__ == "__main__":
    main()
