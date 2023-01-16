import tkinter as tk
import socket
import threading


window = tk.Tk()
window.title("Sever")

# Top frame consisting of two buttons widgets (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Conectar", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Middle frame consisting of two labels for displaying the host and port info
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# The client frame shows the client area
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="Lista de clientes").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=15, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8888
client_name = " "
clients = []
clients_names = []


# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT # code is fine without this
    btnStart.config(state=tk.DISABLED)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)
    server.setblocking(False)
    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Dirección: " + HOST_ADDR
    lblPort["text"] = "Puerto: " + str(HOST_PORT)


# Stop server function
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)


def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)

        # use a thread so as not to clog the gui thread
        threading._start_new_thread(send_receive_client_message, (client, addr))


# Function to receive message from current client AND
# Send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
    client_msg = " "

    # send welcome message to client
    client_name  = client_connection.recv(4096).decode()
    welcome_msg = "Bienvenido " + client_name + ". Escribe 'exit' para salir o <Usuario> seguido del mensaje para un mensaje privado"
    client_connection.send(welcome_msg.encode())

    clients_names.append(client_name)

    update_client_names_display(clients_names)  # update client names display


    while True:
        data = client_connection.recv(4096).decode()
        if not data: break
        if data == "/salir": break
        if data[0] == "<":
            idx = get_client_index(clients,client_connection)
            for name in clients_names:
                if f"<{name}>" in data:
                    print(f"mensaje privado para {name} de {clients_names[idx]}")
                    counter = 0
                    clients_msg = data.split('>')[1];
                    print(clients_msg)
                    sending_client_name = clients_names[idx]
                    server_msg = str("[Privado] " + sending_client_name + "->" + clients_msg)
                    counter2 = 0
                    for  c in clients_names:
                        if c == name:
                            idx2 = counter2
                        else:
                            counter2 += 1
                    clients[idx2].send(server_msg.encode())
                    

        else:
            client_msg = data

            idx = get_client_index(clients, client_connection)
            sending_client_name = clients_names[idx]

            for c in clients:
                if c != client_connection:
                    server_msg = str(sending_client_name + "->" + client_msg)
                    c.send(server_msg.encode())

    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    server_msg = "BYE!"
    client_connection.send(server_msg.encode())
    client_connection.close()

    update_client_names_display(clients_names)  # update client names display


# Return the index of the current client in the list of clients
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Update client name display when a new client connects OR
# When a connected client disconnects
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()