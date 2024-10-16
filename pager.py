import asyncio

# Handle the clients connection to the server
clients= []
async def handle_clients(reader, writer):
    addr= writer.get_extra_info('peername')
    clients.append(writer)

    print(f"New connection from {addr}")

    while True:
        try:
            data= await reader.read(100)
            if not data:
                break
            message= data.decode()
            writer.write('ASK'.encode())
            print(f"Received {message} from {addr}")

            for client in clients:
                if client != writer:
                    client.write(f"{addr} says {message}".encode())
                    await client.drain()
        except asyncio.CancelledError:
            pass  

    print(f"Closing connection from {addr}")
    writer.close()
    await writer.wait_closed()
    clients.remove(writer)


# Handle server
async def start_server():
    server= await asyncio.start_server(handle_clients, '127.0.0.1', 8888)
    addr= server.sockets[0].getsockname()
    print(f"Server on {addr!r}")

    async with server:
        await server.serve_forever()

# Send a message
async def send_message(writer):
    while True:
        message= input("Enter a message: ")
        writer.write(message.encode())
        await writer.drain()

# Receive a message
async def receive_message(reader):
    while True:
        data= await reader.read(1024)
        if not data:
            break
        message= data.decode()
        print(f"Message received: {message}")
    

# Handle connection
async def client_connection():
    await asyncio.sleep(2)
    reader, writer= await asyncio.open_connection('127.0.0.1', 8888)
    print("Connected to the server")
    await asyncio.gather(send_message(writer), receive_message(reader))


async def main():
    choice= input("server or client (c/s)? ")
    if choice == 's':
        await start_server()
    elif choice == 'c':
        await client_connection()

asyncio.run(main())