import csv
import json
import os
from re import L
import socket
from threading import Thread
from multiprocessing import Process


def listener(socket):
    while True:
        data = socket.recv(8192).decode("utf-8")
        print("\n>=< ", data)
        if data == "exit":
            keep_running = False
            for thread in active_threads:
                thread.keep_running = False


class thread(Thread):
    def __init__(self, ip, id):
        Thread.__init__(self)
        self.ip = ip
        self.id = id
        self.keep_running = True
        print("\n[+] Nouveau client connecté. Thread démarré sur {}:25115\n".format(ip, 25115))

    def run(self, connection, serv_msg):
        if serv_msg == 1:
            connection.send(bytes("1", "utf-8"))
            while True:
                l = Process(target=listener, args=(connection,))
                l.start()
                if self.keep_running == False:
                    self.keep_running = True
                    break
                else:
                    msg = input("\n")
                    connection.send(bytes(msg, "utf-8"))
                    if msg.lower() == "exit":
                        break
            del(active_threads[int(self.id)])
            print("\nConnexion fermée !\n")
        elif serv_msg == 2:
            connection.send(bytes("2", "utf-8"))
        else:
            connection.send(bytes("0", "utf-8"))


def regenerate_user_config (force_regeneration):
    if os.path.exists("./user.json") and force_regeneration == False:
        with open("./user.json", "r") as user_config_file:
            JSONcontent = user_config_file.read()
            content = json.loads(JSONcontent)
            try:
                content["name"], content["description"], content["ip"], content["status"], content["type"]
            except KeyError:
                print("\nCorruption du fichier de configuration détectée ! Le fichier a été régénéré. Désolé pour la gêne occasionnée.\n")
                regenerate_user_config(True)
            else:
                if len(content) > 5:
                    print("\nCorruption du fichier de configuration détectée ! Le fichier a été régénéré. Désolé pour la gêne occasionnée.\n")
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
            "status": "online",
            "type": "user"
        }
        with open("./user.json", "w") as user_config_file:
            json.dump(user, user_config_file)
        print("\nNouveau fichier de configuration utilisateur généré. N'oubliez pas de jeter un coup d'oeil à vos paramètres pour les modifier.\n")


def initialize (force_user_config_regeneration):
    regenerate_user_config(force_user_config_regeneration)
    modify_user_status(1)


def add_contact (name, description, ip, type):
    if not os.path.exists("./contacts.csv"):
        with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
    with open("./contacts.csv", "a") as contacts_file:
        writer = csv.writer(contacts_file, delimiter = " ", quotechar = "\"", quoting = csv.QUOTE_MINIMAL)
        writer.writerow([str(name), str(description), str(ip), "offline", str(type)])
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
    print("\nLa valeur [{}] a été affectée à la clé [{}] avec succès !\n".format(value, key))


def get_user_config():
    with open("./user.json", "r") as user_config_file:
        JSONcontent = user_config_file.read()
        content = json.loads(JSONcontent)
        user_config_file.close()
        return content


def display_contacts():
    if not os.path.exists("./contacts.csv"):
        with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
    with open("./contacts.csv", "r") as contacts_file:
        reader = csv.reader(contacts_file, delimiter=" ", quotechar = "\"")
        i = 1
        for row in reader:
            if len(row) > 0:
                print("\nContact numéro {}:\n\tNom: {}\n\tDescription: {}\n\tIP: {}\n\tStatut: {}\n\tType: {}\n".format(str(i), str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4])))
                i = i + 1
            else:
                print("\n")


def getContactInfo(name):
    if not os.path.exists("./contacts.csv"):
        with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
    with open("./contacts.csv", "r") as contacts_file:
        reader = csv.reader(contacts_file, delimiter=" ", quotechar = "\"")
        for row in reader:
            if len(row) > 0 and str(row[0]).lower() == name.lower():
                contact = {
                    "name": str(row[0]),
                    "description": str(row[1]),
                    "ip": str(row[2]),
                    "status": str(row[3]),
                    "type": str(row[4])
                }
                break
        if contact:
            return contact
        else:
            return False


def modify_user_status(user_choice = -1):
    if user_choice == -1:
        user_choice = int(input("\nVoulez-vous être en ligne ou hors-ligne ? [1/2]\n"))
    if user_choice == 1:
        modify_user_config("status", "online")
    else:
        modify_user_config("status", "offline")
    print("\nStatut modifié avec succcès !\n")


def start_server(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((str(ip), 25115))
    while True:
        s.listen(999999999)
        print("\nServeur démarré sur {}:25115\n".format(str(ip)))
        connection, (ip, port) = s.accept()
        newthread = thread(ip, len(active_threads))
        if get_user_config()["status"] == "offline":
            newthread.run(connection, 0)
        elif get_user_config()["type"] == "client" and len(active_threads) > 0:
            newthread.run(connection, 2)
        else:
            active_threads.append(newthread)
            newthread.run(connection, 1)
        if len(active_threads) <= 0:
            break
    for t in active_threads:
        t.join()


def start_client(ip):
    msg = ""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((str(ip), 25115))
    data = s.recv(8192).decode("utf-8")
    if data == ("1"):
        print("\nConnection à l'hôte réussie !\n")
        while True:
            msg = input("\n")
            s.send(bytes(msg, "utf-8"))
            if msg.lower() == "exit":
                break
            l = Process(target=listener, args=(s,))
            l.start()
            if keep_running == False:
                keep_running = True
                break
        s.close()
        print("\nConnexion fermée !\n")
    elif data == ("2"):
        print("\nConnection à l'hôte impossible : l'hôte a atteint le nombre maximal de connexions.\n")
        s.close()
    else:
        print("\nConnection à l'hôte impossible : l'hôte est hors-ligne.\n")
        s.close()



# def update_contacts_status():


# def encrypt_message(message, RSA_key):


# def decrypt_message(message, RSA_key):


if __name__ == "__main__":
    initialize(False)
    active_threads = []
    keep_running = True
    print("Bienvenue Sur EMT.\n")

    while True:
        user_choice = int(input("\nQuel Est Votre Souhait ?\n\t1/ Héberger un salon;\n\t2/ Me connecter à un salon;\n\t3/ Modifier mes réglages;\n\t4/ Afficher mes contacts;\n\t5/ Ajouter un contact;\n\t6/ Modifier mon statut;\n\t7/ Afficher l'aide;\n\t8/ C'est quoi ETM ?;\n\t9/ Quitter ETM;\n\n"))

        if user_choice == 1:
            choice = str(input("\nVoulez-vous utiliser l'adresse IP enregistrée ? [o / n]\n"))
            if choice.lower() == "o":
                user_config = get_user_config()
                start_server(user_config["ip"])
            else:
                ip = str(input("\nQuelle adresse IP voulez-vous utiliser ?\n"))
                start_server(ip)

        elif user_choice == 2:
            choice = int(input("\nVoulez-vous vous connecter à un contact enregistré ou non enregistré ? [1 / 2]\n"))
            if choice == 1:
                name = str(input("\nQuel est le nom de votre contact ?\n"))
                contact = getContactInfo(name)
                if contact != False:
                    start_client(contact["ip"])
                else:
                    print("\nVous n'avez aucun contact enregistré à ce nom !\n")
            else:
                ip = str(input("\nQuelle est l'adresse IP de votre contact ?\n"))
                start_client(ip)

        elif user_choice == 3:
            key = str(input("\nQuelle clé voulez-vous modifier ? [description / name / ip / type]\n"))
            value = str(input("\nQuelle nouvelle valeur voulez-vous attribuer à la clé {} ?\n".format(key)))
            modify_user_config(key, value)

        elif user_choice == 4:
            display_contacts()

        elif user_choice == 5:
            contact_name = str(input("\nQuel est le nom de votre contact ?\n"))
            contact_description = str(input("\nQuelle est la desription de votre contact ?\n"))
            contact_ip = str(input("\nVeuillez entrer l'adresse ip de votre contact.\n"))
            contact_type = str(input("\nVeuillez entrer le type de votre contact.\n"))
            add_contact(contact_name, contact_description, contact_ip, contact_type)

        elif user_choice == 6:
            pass

        elif user_choice == 7:
            pass

        elif user_choice == 8:
            pass

        elif user_choice == 9:
            print("\nAu revoir !")
            modify_user_status(2)
            break