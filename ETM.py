from asyncio.windows_events import NULL
import csv
import json
import os
import socket
from threading import Thread
from multiprocessing import Process
import datetime
try:
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Cipher import PKCS1_OAEP
except:
    os.system("pip install pycryptodome")
    os.system("pip install pycryptodomex")
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Cipher import PKCS1_OAEP


active_threads = []
key = RSA.generate(2048)
public_key = key.public_key().export_key()
contact_public_key = b""
contact_cipher = PKCS1_OAEP.new(public_key)
cipher = PKCS1_OAEP.new(public_key)


def listener(socket, pair_ip):
    while True:
        try:
            data = socket.recv(8192)
            print("\n=> [{}] {}\n\t{}".format(str(pair_ip), str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')), cipher.decrypt(data)))
        except ConnectionResetError:
            modify_cache("stop_listening")
            print("\nVotre correspondant s'est déconnecté ! Appuyez sur Espace pour continuer.\n")
            break
        if data.lower() == "exit":
            modify_cache("stop_listening")
            print("\nVotre correspondant s'est déconnecté ! Appuyez sur Espace pour continuer.\n")
            break
        else:
            modify_cache("save_message", "[{}] {}".format(str(pair_ip), str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))), cipher.decrypt(data))


class thread(Thread):
    def __init__(self, ip, id, client_ip):
        Thread.__init__(self)
        self.ip = ip
        self.id = id
        self.client_ip = client_ip
        print("\n[+] Nouveau client connecté ({}:25115) ! Dès que vous voudrez quitter la discussion, entrez Exit.\n".format(client_ip, 25115))

    def run(self, connection, serv_msg):
        if serv_msg == 1:
            try:
                connection.send(bytes("1", "utf-8"))
                contact_public_key = connection.recv(8192)
                connection.send(public_key)
                contact_cipher = PKCS1_OAEP.new(RSA.importKey(contact_public_key))
            except ConnectionResetError:
                pass          
            modify_cache("reset_cache")
            l = Process(target=listener, args=(connection, self.client_ip,))
            l.start()
            while True:
                msg = input("\n")
                modify_cache("save_message", "[{}] {}".format(str(self.ip), str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))), msg)
                try:
                    connection.send(contact_cipher.encrypt(bytes(msg, "utf-8")))
                except ConnectionResetError:
                    pass
                if msg.lower() == "Exit":
                    modify_cache("stop_listening")
                if modify_cache("get_listening_status") == False:
                    user_choice = str(input("\nVoulez-vous enregistrer cette conversation ? [O/N]\n"))
                    if user_choice.lower() == "o":
                        modify_cache("save_conversation")
                    break
            del(active_threads[int(self.id)])
            print("\nConnexion fermée !\n")
        else:
            try:
                connection.send(bytes("0", "utf-8"))
            except ConnectionResetError:
                pass


def regenerate_user_config (force_regeneration):
    if os.path.exists("./user.json") and force_regeneration == False:
        with open("./user.json", "r") as user_config_file:
            JSONcontent = user_config_file.read()
            content = json.loads(JSONcontent)
            try:
                content["name"], content["description"], content["ip"], content["status"]
            except KeyError:
                print("\nCorruption du fichier de configuration détectée ! Le fichier a été régénéré. Désolé pour la gêne occasionnée.\n")
                regenerate_user_config(True)
            else:
                if len(content) > 4:
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
            "status": "online"
        }
        with open("./user.json", "w") as user_config_file:
            json.dump(user, user_config_file)
            user_config_file.close()
        print("\nNouveau fichier de configuration utilisateur généré. N'oubliez pas de jeter un coup d'oeil à vos paramètres pour les modifier.\n")


def initialize (force_user_config_regeneration):
    regenerate_user_config(force_user_config_regeneration)
    modify_user_status(1)
    modify_cache("reset_cache")


def modify_cache(request, key="", value=""):
    if not os.path.exists("./cache.json"):
        with open("./cache.json", "x") as cache_file: cache_file.close()

    if request == "reset_cache":
        with open("./cache.json", "w") as cache_file:
            cache_template = {
                "keep_listening": True,
                "saved_conversation": {}
            }
            json.dump(cache_template, cache_file)
            cache_file.close()
    elif request == "save_message":
        with open("./cache.json", "r") as cache_file:
            JSONcontent = cache_file.read()
            content = json.loads(JSONcontent)
            cache_file.close()
        content["saved_conversation"][str(key)] = str(value)
        with open("./cache.json", "w") as cache_file:
            json.dump(content, cache_file)
            cache_file.close()
    elif request == "save_conversation":
        with open("./cache.json", "r") as cache_file:
            JSONcontent = cache_file.read()
            content = json.loads(JSONcontent)
            cache_file.close()
        if not os.path.exists("./saved_conversation.txt"):
            with open("./saved_conversation.txt", "x") as saved_conversation_file: saved_conversation_file.close()
        else:
            with open("./saved_conversation.txt", "w") as saved_conversation_file: saved_conversation_file.close()
        content = content["saved_conversation"].items()
        for elt in content:
            with open("./saved_conversation.txt", "a") as saved_conversation_file:
                saved_conversation_file.write("\n# {} =>".format(str(elt[0])))
                saved_conversation_file.close()
            with open("./saved_conversation.txt", "a") as saved_conversation_file:
                saved_conversation_file.write(str("\n\t\" {} \"\n".format(str(elt[1]))))
                saved_conversation_file.close()
        if os.path.exists("./saved_conversation.txt"):
            print("\nConversation sauvegardée avec succès dans saved_conversation.txt !\n")
        else:
            print("\nÉchec lors de la sauvegarde de la conversation !\n")
    elif request == "stop_listening":
        with open("./cache.json", "r") as cache_file:
            JSONcontent = cache_file.read()
            content = json.loads(JSONcontent)
            cache_file.close()
        content["keep_listening"] = False
        with open("./cache.json", "w") as cache_file:
            json.dump(content, cache_file)
            cache_file.close()
    elif request == "get_listening_status":
        with open("./cache.json", "r") as cache_file:
            JSONcontent = cache_file.read()
            content = json.loads(JSONcontent)
            cache_file.close()
        return content["keep_listening"]


def add_contact (name, description, ip):
    if not os.path.exists("./contacts.csv"):
        with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
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


def modify_user_status(user_choice=-1):
    if user_choice == -1:
        user_choice = int(input("\nVoulez-vous être en ligne ou hors-ligne ? [1/2]\n"))
    if user_choice == 1:
        modify_user_config("status", "online")
    else:
        modify_user_config("status", "offline")
    print("\nStatut modifié avec succès !\n")


def start_server(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((str(ip), 25115))
    while True:
        s.listen(1)
        print("\nServeur démarré sur {}:25115\n".format(str(ip)))
        connection, client_ip = s.accept()
        newthread = thread(ip, len(active_threads), client_ip)
        if get_user_config()["status"] == "offline":
            newthread.run(connection, 0)
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
        s.send(public_key)
        contact_public_key = s.recv(8192)
        contact_cipher = PKCS1_OAEP.new(RSA.importKey(contact_public_key))
        print("\nConnection à l'hôte réussie ! Dès que vous voudrez quitter la discussion, entrez Exit.\n")
        modify_cache("reset_cache")
        l = Process(target=listener, args=(s, ip,))
        l.start()
        while True:
            msg = input("\n")
            modify_cache("save_message", "[{}] {} ".format(str(ip), str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))), msg)
            try:
                s.send(contact_cipher.encrypt(bytes(msg, "utf-8")))
            except ConnectionResetError:
                pass
            if msg.lower() == "exit":
                modify_cache("stop_listening")
            if modify_cache("get_listening_status") == False:
                user_choice = str(input("\nVoulez-vous enregistrer cette conversation ? [O/N]\n"))
                if user_choice.lower() == "o":
                    modify_cache("save_conversation")
                break
        s.close()
        print("\nConnexion fermée !\n")
    else:
        print("\nConnection à l'hôte impossible : l'hôte est hors-ligne.\n")
        s.close()


if __name__ == "__main__":
    initialize(False)
    print("\nBienvenue Sur ETM.\n")

    while True:
        user_choice = int(input("\nQuel Est Votre Souhait ?\n\t1/ Héberger un salon ;\n\t2/ Me connecter à un salon ;\n\t3/ Modifier mes réglages ;\n\t4/ Afficher mes contacts ;\n\t5/ Ajouter un contact ;\n\t6/ Modifier mon statut ;\n\t7/ Afficher l'aide ;\n\t8/ C'est quoi ETM ? ;\n\t9/ Quitter ETM ;\n\n"))

        if user_choice == 1:
            choice = str(input("\nVoulez-vous utiliser l'adresse IP enregistrée ? [O/N]\n"))
            if choice.lower() == "o":
                user_config = get_user_config()
                start_server(user_config["ip"])
            else:
                ip = str(input("\nQuelle adresse IP voulez-vous utiliser ?\n"))
                start_server(ip)

        elif user_choice == 2:
            choice = int(input("\nVoulez-vous vous connecter à un contact enregistré ou non enregistré ? [1/2]\n"))
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
            add_contact(contact_name, contact_description, contact_ip)

        elif user_choice == 6:
            choice = int(input("\nVoulez-vous passer en mode en ligne ou en mode hors-ligne ? [1/2]\n"))
            modify_user_status(choice)

        elif user_choice == 7:
            print("\nBientôt\n")

        elif user_choice == 8:
            print("\nBientôt\n")

        elif user_choice == 9:
            print("\nAu revoir !")
            modify_user_status(2)
            break