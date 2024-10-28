import asyncio

# Handle client connections with the server
clients= []
async def handle_connections(reader, writer):
    addr= writer.get_extra_info('peername')
    print(f"Connected to {addr[1]}")
    clients.append(writer)

    try:
        while True:
            data= await reader.read(100)
            if not data:
                break
            # Receive a message from a client
            message= data.decode()
            print(f"{message} from {addr[1]}")

            if message != 'exit':
                # Send a response to the sender
                response= "Message Received"
                writer.write(response.encode())
                await writer.drain()

                for client in clients:
                    if client != writer:
                        client.write(f"{addr[1]} says {message}".encode())
                        await client.drain()

            if message == 'exit':
                # Send a response
                response= "\nGoodbye"
                writer.write(response.encode())
                await writer.drain()
                # Send a message to other clients
                for client in clients:
                    if client != writer:
                        client.write(f"{addr[1]} has left".encode())
                        await client.drain()
                # Close the connection
                writer.close()
                await writer.wait_closed()
                break

    except asyncio.CancelledError:
        print(f"Closing connection with {addr[1]}")

    clients.remove(writer)
    print(f"Connection closed with {addr[1]}")




# Start a server
async def start_server():
    server= await asyncio.start_server(handle_connections, '127.0.0.1', 8888)
    addr= server.sockets[0].getsockname()
    print(f"Server on {addr}")

    # Let the server work forever until it's stopped manually
    async with server:
        await server.serve_forever()


# Write and send messages
async def send_message(writer):
    while True:
        message= await asyncio.to_thread(input, "Write a message: \n")

        if message.lower() == 'exit':
            writer.write("exit".encode())
            await writer.drain()
            break

        writer.write(message.encode())
        await writer.drain()
        await asyncio.sleep(1)

# Read and receive messages
async def receive_message(reader):
    while True:
        data= await reader.read(100)
        if not data:
            break
        message= data.decode()
        print(f"{message}")


# Create connection with the server
async def open_connection():
    # Open connection with the server socket
    reader, writer= await asyncio.open_connection('127.0.01', 8888)
    addr= writer.get_extra_info('peername')
    print(f"Connected to the server {addr}")
    # receive and send messages to the server
    await asyncio.gather(receive_message(reader), send_message(writer))


# Main Connection
async def main():
    choice= input("Client or server c/s? ")
    if choice == "s":
        await start_server()
    elif choice == "c":
        await open_connection()

asyncio.run(main())

