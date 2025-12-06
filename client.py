import socket
import matplotlib.pyplot as plt
import pickle

# Define the server IP address and port number
SERVER_IP = '192.168.0.194'
SERVER_PORT = 5000

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_IP, SERVER_PORT))

# Set up the plot
fig, ax = plt.subplots()
plt.ion()
# x_data = []
# y_data = []
# plot, = ax.plot(x_data, y_data)

# Receive real-time data from the server
while True:
    # Receive the data from the server
    data = client_socket.recv(4096)

    buffer = pickle.loads(data)
    y_data = buffer
    x_data = range(len(buffer))
    ax.clear()
    plot, = ax.plot(x_data, y_data)

    # try:
    #     value = float(data)
    # except ValueError:
    #     continue

    # Add the received data to the plot
    # x_data.append(len(x_data))
    # y_data.append(value)
    plot.set_data(x_data, y_data)

    # Update the plot
    plt.xlim([max(0, len(x_data) - 50), len(x_data)])
    plt.ylim([min(y_data), max(y_data)])
    plt.draw()
    plt.pause(0.01)

    # Print the received data
    print(f"Received data: {pickle.loads(data)}")

# Close the socket
client_socket.close()