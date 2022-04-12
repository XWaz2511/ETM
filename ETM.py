import csv
import json
import datetime
import os
import select
import socket as sock
import sys
import queue


def regenerate_user_config (force_regeneration):
    if os.path.exists("./user.json") and force_regeneration == False:
        with open("./user.json", "r") as user_config_file:
            JSONcontent = user_config_file.read()
            content = json.loads(JSONcontent)
            try:
                content["name"], content["description"], content["ip"], content["status"]
            except KeyError:
                print("Corruption du fichier de configuration détectée ! Le fichier a été régénéré. Désolé pour la gêne occasionnée.\n")
                regenerate_user_config(True)
            else:
                if len(content) > 4:
                    print("Corruption du fichier de configuration détectée ! Le fichier a été régénéré. Désolé pour la gêne occasionnée.\n")
                    regenerate_user_config(True)
                else:
                    pass
    else:
        if os.path.exists("./user.json"):
            with open("./user.json", "w") as user_config_file: user_config_file.close()
        else:
            with open("./user.json", "x") as user_config_file: user_config_file.close()
        user = {
            "name": "Newbie",
            "description": "null",
            "ip": "127.0.0.1",
            "status": "online"
        }
        with open("./user.json", "w") as user_config_file:
            json.dump(user, user_config_file)
        print("Nouveau fichier de configuration utilisateur généré. N'oubliez pas de jeter un coup d'oeil à vos paramètres pour les modifier.\n")


def initialize (force_user_config_regeneration):
    regenerate_user_config(force_user_config_regeneration)
    modify_user_status(1)


def write_message (message, author, room):
    if not os.path.exists("./Messages"):
        os.mkdir("Messages")
    else:
        pass
    if not os.path.exists("./Messages/{}.csv".format(str(room))):
        file = open("./Messages/{}.csv".format(str(room)), "x")
        file.close()
    else:
        pass
    with open("./Messages/{}.csv".format(str(room)), "a") as message_file:
        writer = csv.writer(message_file, delimiter = " ", quotechar = "\"", quoting = csv.QUOTE_MINIMAL)
        writer.writerow([str(datetime.datetime.now()), str(author), str(message)])


def read_messages (room):
    with open("./Messages/{}.csv".format(str(room)), newline = "") as messages_file:
        reader = csv.reader(messages_file, delimiter = " ", quotechar = "\"")
        for row in reader:
            print(" ".join(row) + "\n")


def add_contact (name, description, ip):
    if not os.path.exists("./contacts.csv"):
        with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
    else:
        pass
    with open("./contacts.csv", "a") as contacts_file:
        writer = csv.writer(contacts_file, delimiter = " ", quotechar = "\"", quoting = csv.QUOTE_MINIMAL)
        writer.writerow([str(name), str(description), str(ip), "offline"])
        contacts_file.close()
    print("\nContact crée avec succès !\n")


def modify_user_config(key: str, value: str):
    if not os.path.exists("./user.json"):
        regenerate_user_config(False)
    with open("./user.json", "r") as user_config_file:
        JSONcontent = user_config_file.read()
        content = json.loads(JSONcontent)
        content[key] = value
        user_config_file.close()
    with open("./user.json", "w") as user_config_file:
        json.dump(content, user_config_file)
        user_config_file.close()
    print("La valeur [{}] a été affectée à la clé [{}] avec succès !".format(value, key))


def display_contacts():
    with open("./contacts.csv", "r") as contacts_file:
        reader = csv.reader(contacts_file, delimiter=" ", quotechar = "\"")
        i = 1
        for row in reader:
            if len(row) > 0:
                print("Contact numéro {}:\n\tNom: {}\n\tDescription: {}\n\tIP: {}\n\tStatut: {}".format(str(i), str(row[0]), str(row[1]), str(row[2]), str(row[3])))
                i = i + 1
            else:
                print("\n")


def modify_user_status(user_choice = -1):
    if user_choice == -1:
        user_choice = int(input("\nVoulez-vous être en ligne ou hors-ligne ? [1/2]\n"))
    if user_choice == 1:
        modify_user_config("status", "online")
    else:
        modify_user_config("status", "offline")
    print("\nStatut modifié avec succcès !\n")


def create_client_socket(ip, port, msg):
    s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    s.connect((str(ip), int(port)))
    s.sendall(bytes(str(msg), "utf-8"))
    data = s.recv(1024)
    s.close()
    print(repr(data), "ok")


def create_server_socket(ip, port):
    s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    s.setblocking(0)
    s.bind((str(ip), int(port)))
    s.listen(15)
    inputs = [s]
    outputs = []
    msg = {}
    print("\nServeur ouvert avec succès sur {}:{}\n".format(str(ip), str(port)))

    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        for socket in readable:
            if socket is s:
                connexion, client_addr = socket.accept()
                connexion.setblocking(0)
                msg[connexion] = queue.Queue()
            else:
                data = sock.recv(1024)
                if data:
                    print(data)
                    msg[socket].put(data)
                    if socket not in outputs:
                        outputs.append(socket)
                    else:
                        if socket in outputs:
                            outputs.remove(socket)
                        inputs.remove(socket)
                        socket.close()
                        del msg[socket]

        for socket in writable:
            try:
                next_msg = msg[s].get_nowait()
            except Queue.Empty:
                outputs.remove(socket)
            else:
                socket.send(next_msg)

        for socket in exceptional:
            inputs.remove(socket)
            if socket in outputs:
                outputs.remove(s)
            socket.close()
            del msg[socket]


# def update_contacts_status():


# def encrypt_message(message, RSA_key):


# def decrypt_message(message, RSA_key):


if __name__ == "__main__":
    initialize(False)
    print("Bienvenue Sur EMT.")

    while True:
        user_choice = int(input("Quel Est Votre Souhait ?\n\t1/ Me connecter à un salon;\n\t2/ Héberger un salon;\n\t3/ Modifier mes réglages;\n\t4/ Afficher mes contacts;\n\t5/ Ajouter un contact;\n\t6/ Modifier mon statut;\n\t7/ Afficher l'aide;\n\t8/ C'est quoi ETM ?;\n\t9/ Quitter ETM;"))

        if user_choice == 1:
            ip = str(input("\nQuelle est votre IP ?\n"))
            port = int(input("\nQuel port voulez-vous utiliser ?\n"))
            create_server_socket(ip, port)

        elif user_choice == 2:
            ip = str(input("Quelle ip"))
            port = int(input("Quel port"))
            msg = str(input("Message"))
            create_client_socket(ip, port, msg)

        elif user_choice == 3:
            key = str(input("Quelle clé voulez-vous modifier ? [description / name / ip]"))
            value = str(input("Quelle nouvelle valeur voulez-vous attribuer à la clé {} ?".format(key)))
            modify_user_config(key, value)

        elif user_choice == 4:
            display_contacts()

        elif user_choice == 5:
            contact_name = str(input("Quel est le nom de votre contact ?"))
            contact_description = str(input("Quelle est la desription de votre contact ?"))
            contact_ip = str(input("Veuillez entrer l'adresse ip de votre contact."))
            add_contact(contact_name, contact_description, contact_ip)

        elif user_choice == 6:
            pass

        elif user_choice == 7:
            pass

        elif user_choice == 8:
            pass

        elif user_choice == 9:
            print("Au revoir !")
            modify_user_status(2)
            break