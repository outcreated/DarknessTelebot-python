import socket
import asyncio
import threading
from database import requests

HOST = "94.241.168.39"  # адрес сервера
PORT = 26002        # порт сервера


def init():
    thread = threading.Thread(target=create)
    thread.start()


def create():
    asyncio.run(create_socket())


async def create_socket():
    print(f"Сокет успешно создан, ожидание подключения по: {HOST}:{PORT}")
    while True:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        conn, addr = server_socket.accept()
        with conn:
            # print('Получено подключение от', addr)
            data = conn.recv(1024)
            print('Новая авторизация: ', data.decode())
            request = data.decode()

            id_ = request.split(":")[0]
            product_key = str(request.split(":")[1]).split("$")[0]
            hwid = str(request.split(":")[1]).split("$")[1]

            user = await requests.get_user_by_telegram_id(int(id_))
            product = await requests.get_product_by_key(
                product_key=product_key)

            if not product:
                response = "ERROR"
                conn.send(response.encode())
            else:
                if not user:
                    response = "ERROR"
                    conn.send(response.encode())
                else:
                    if int(user.current_products.split(":")[1]) > 0:
                        if user.user_hwid == "":
                            await requests.update_user_hwid(hwid, id_)
                            response = f"OK:{product_key}"
                            conn.send(response.encode())

                        elif user.user_hwid == hwid:
                            response = f"OK:{product_key}"
                            conn.send(response.encode())
            conn.close()
