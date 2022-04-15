from csv import writer, QUOTE_MINIMAL, reader
from json import loads, dump
import multiprocessing
from os import system, path
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from multiprocessing import Process
from datetime import datetime
from time import sleep

try:
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Cipher import PKCS1_OAEP
except:
    system("pip install pycryptodome")
    system("pip install pycryptodomex")
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Cipher import PKCS1_OAEP

if multiprocessing.get_start_method() != "spawn":
    multiprocessing.set_start_method("spawn")


class thread(Thread):
    def __init__(self, ip, id, client_ip):
        Thread.__init__(self)
        self.ip = ip
        self.id = id
        self.client_ip = client_ip

    def run(self, connection, serv_msg, client_ip):
        if serv_msg == 1:
            try:
                connection.send(bytes("1", "utf-8"))
                keys.append(connection.recv(16384))
                connection.send(keys[2])
                keys.append(PKCS1_OAEP.new(RSA.import_key(keys[3])))
            except ConnectionResetError:
                pass          
            modify_cache("reset_cache")
            l = Process(target=listener, args=(connection, self.client_ip, keys[0].export_key(),))
            l.start()
            print("\n[+] Nouveau client connecté ({}:25115) ! Dès que vous voudrez quitter la discussion, entrez Exit.\n".format(client_ip))
            while True:
                msg = input("\n=> ")
                modify_cache("save_message", "[{}] {}".format(str(self.ip), str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))), msg)
                try:
                    msg = keys[4].encrypt(bytes(msg, "utf-8"))
                    print("\nMessage crypté : ", msg)
                    connection.send(msg)
                except ConnectionResetError:
                    pass
                if msg.lower() == "Exit":
                    modify_cache("stop_listening")
                if modify_cache("get_listening_status") == False:
                    user_choice = str(input("\n[?] Voulez-vous enregistrer cette conversation ? [O/N]\n=> "))
                    if user_choice.lower() == "o":
                        modify_cache("save_conversation")
                    break
            del(active_threads[int(self.id)])
            print("\n[!] Connexion fermée !\n")
            sleep(0.5)
        else:
            try:
                connection.send(bytes("0", "utf-8"))
            except ConnectionResetError:
                pass
            print("\n[X] Un client ({}:25115) a essayé de se connecter mais a été rejeté étant donné que vous êtes en mode hors-ligne. Utilisez l'option 3 du menu pour changer votre statut.\n".format(client_ip))
            sleep(0.5)


def modify_cache(request, key="", value=""):
    if not path.exists("./cache.json"):
        with open("./cache.json", "x") as cache_file: cache_file.close()

    if request == "reset_cache":
        with open("./cache.json", "w") as cache_file:
            cache_template = {
                "keep_listening": True,
                "saved_conversation": {}
            }
            dump(cache_template, cache_file)
            cache_file.close()
        print("\n[!] Le cache a été vidé !\n")
        sleep(0.5)
    elif request == "save_message":
        with open("./cache.json", "r") as cache_file:
            JSONcontent = cache_file.read()
            content = loads(JSONcontent)
            cache_file.close()
        content["saved_conversation"][str(key)] = str(value)
        with open("./cache.json", "w") as cache_file:
            dump(content, cache_file)
            cache_file.close()
    elif request == "save_conversation":
        with open("./cache.json", "r") as cache_file:
            JSONcontent = cache_file.read()
            content = loads(JSONcontent)
            cache_file.close()
        if not path.exists("./saved_conversation.txt"):
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
        if path.exists("./saved_conversation.txt"):
            print("\n[!] Conversation sauvegardée avec succès dans saved_conversation.txt !\n")
            sleep(0.5)
        else:
            print("\n[X] Échec lors de la sauvegarde de la conversation !\n")
            sleep(0.5)
    elif request == "stop_listening":
        with open("./cache.json", "r") as cache_file:
            JSONcontent = cache_file.read()
            content = loads(JSONcontent)
            cache_file.close()
        content["keep_listening"] = False
        with open("./cache.json", "w") as cache_file:
            dump(content, cache_file)
            cache_file.close()
    elif request == "get_listening_status":
        with open("./cache.json", "r") as cache_file:
            JSONcontent = cache_file.read()
            content = loads(JSONcontent)
            cache_file.close()
        return content["keep_listening"]


def initialize (force_user_config_regeneration):
    print("[...] Génération de la clé RSA 4096 bits... Cette opération peut durer une vingtaine de secondes suivant votre ordinateur.\n")
    keys.append(RSA.generate(4096))
    print("\n[!] La clé a été générée avec succès !\n")
    sleep(0.5)
    keys.append(" ")
    keys.append(keys[0].public_key().export_key())
    regenerate_user_config(force_user_config_regeneration)
    modify_user_status(1)
    modify_cache("reset_cache")


def listener(socket, pair_ip, key):
    private_key = PKCS1_OAEP.new(RSA.import_key(key))
    while True:
        try:
            crypted_data = socket.recv(16384)
            print("Message crypté: ", crypted_data)
            decrypted_data = private_key.decrypt(crypted_data).decode("utf-8")
            print("\n=> [{}] {}\n\t{}".format(str(pair_ip), str(datetime.now().strftime('%d-%m-%Y %H:%M:%S')), decrypted_data))
        except ConnectionResetError:
            modify_cache("stop_listening")
            print("\n[!] Votre correspondant s'est déconnecté ! Appuyez sur une touche pour continuer.\n")
            break
        if decrypted_data.lower() == "exit":
            modify_cache("stop_listening")
            print("\n[!] Votre correspondant s'est déconnecté ! Appuyez sur une touche pour continuer.\n")
            break
        else:
            modify_cache("save_message", "[{}] {}".format(str(pair_ip), str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))), decrypted_data)


def start_server(ip):
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind((str(ip), 25115))
    while True:
        s.listen(1)
        print("\n[!] Serveur démarré sur {}:25115\n".format(str(ip)))
        connection, client_infos = s.accept()
        newthread = thread(ip, len(active_threads), client_infos[0])
        if get_user_config()["status"] == "offline":
            newthread.run(connection, 0, client_infos[0])
        else:
            active_threads.append(newthread)
            newthread.run(connection, 1, client_infos[0])
        if len(active_threads) <= 0:
            break
    for t in active_threads:
        t.join()


def start_client(ip):
    msg = ""
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((str(ip), 25115))
        data = s.recv(16384).decode("utf-8")
    except ConnectionRefusedError:
        print("\n[X] Connection à l'hôte impossible : l'hôte est hors-ligne.\n")
        sleep(0.5)
        s.close()
    else:
        if data == ("1"):
            s.send(keys[2])
            keys.append(s.recv(16384))
            keys.append(PKCS1_OAEP.new(RSA.import_key(keys[3])))
            print("\n[!] Connection à l'hôte réussie ! Dès que vous voudrez quitter la discussion, entrez Exit.\n")
            modify_cache("reset_cache")
            l = Process(target=listener, args=(s, ip, keys[0].export_key(),))
            l.start()
            while True:
                msg = input("\n=> ")
                modify_cache("save_message", "[{}] {} ".format(str(ip), str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))), msg)
                try:
                    msg = keys[4].encrypt(bytes(msg, "utf-8"))
                    print("\nMessage crypté : ", msg)
                    s.send(msg)
                except ConnectionResetError:
                    pass
                if msg.lower() == "exit":
                    modify_cache("stop_listening")
                if modify_cache("get_listening_status") == False:
                    user_choice = str(input("\n[?] Voulez-vous enregistrer cette conversation ? [O/N]\n=> "))
                    if user_choice.lower() == "o":
                        modify_cache("save_conversation")
                    break
            s.close()
            print("\n[!] Connexion fermée !\n")
            sleep(0.5)
        else:
            print("\n[X] Connection à l'hôte impossible : l'hôte est hors-ligne.\n")
            sleep(0.5)
            s.close()


def regenerate_user_config (force_regeneration):
    if path.exists("./user.json") and force_regeneration == False:
        with open("./user.json", "r") as user_config_file:
            JSONcontent = user_config_file.read()
            content = loads(JSONcontent)
            try:
                content["name"], content["description"], content["ip"], content["status"]
            except KeyError:
                print("\n[X] Corruption du fichier de configuration détectée ! Le fichier a été régénéré. Désolé pour la gêne occasionnée.\n")
                sleep(0.5)
                regenerate_user_config(True)
            else:
                if len(content) > 4:
                    print("\n[X] Corruption du fichier de configuration détectée ! Le fichier a été régénéré. Désolé pour la gêne occasionnée.\n")
                    sleep(0.5)
                    regenerate_user_config(True)
                else:
                    pass
    else:
        if path.exists("./user.json"):
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
            dump(user, user_config_file)
            user_config_file.close()
        print("\n[!] Nouveau fichier de configuration utilisateur généré. N'oubliez pas de jeter un coup d'oeil à vos paramètres pour les modifier.\n")
        sleep(0.5)


def modify_user_config(key: str, value: str):
    if not path.exists("./user.json"):
        regenerate_user_config(False)
    with open("./user.json", "r") as user_config_file:
        JSONcontent = user_config_file.read()
        content = loads(JSONcontent)
        content[key] = value
        user_config_file.close()
    with open("./user.json", "w") as user_config_file:
        dump(content, user_config_file)
        user_config_file.close()
    print("\n[!] La valeur [{}] a été affectée à la clé [{}] avec succès !\n".format(value, key))
    sleep(0.5)


def modify_user_status(user_choice=-1):
    if user_choice == -1:
        user_choice = int(input("\n[?] Voulez-vous être en ligne ou hors-ligne ? [1/2]\n=> "))
    if user_choice == 1:
        modify_user_config("status", "online")
    else:
        modify_user_config("status", "offline")
    print("\n[!] Statut modifié avec succès !\n")
    sleep(0.5)


def get_user_config():
    with open("./user.json", "r") as user_config_file:
        JSONcontent = user_config_file.read()
        content = loads(JSONcontent)
        user_config_file.close()
        return content


def add_contact (name, description, ip):
    if not path.exists("./contacts.csv"):
        with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
    with open("./contacts.csv", "a") as contacts_file:
        Writer = writer(contacts_file, delimiter = " ", quotechar = "\"", quoting = QUOTE_MINIMAL)
        Writer.writerow([str(name), str(description), str(ip)])
        contacts_file.close()
    print("\n[!] Contact crée avec succès !\n")
    sleep(0.5)


def display_contacts():
    if not path.exists("./contacts.csv"):
        with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
    with open("./contacts.csv", "r") as contacts_file:
        Reader = reader(contacts_file, delimiter=" ", quotechar = "\"")
        i = 1
        for row in Reader:
            if len(row) > 0:
                sleep(0.1)
                print("\n[-] Contact numéro {}:\n\tNom: {}\n\tDescription: {}\n\tIP: {}\n".format(str(i), str(row[0]), str(row[1]), str(row[2])))
                i = i + 1
            else:
                print("\n")


def getContactInfo(name):
    if not path.exists("./contacts.csv"):
        with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
    with open("./contacts.csv", "r") as contacts_file:
        Reader = reader(contacts_file, delimiter=" ", quotechar = "\"")
        for row in Reader:
            if len(row) > 0 and str(row[0]).lower() == name.lower():
                contact = {
                    "name": str(row[0]),
                    "description": str(row[1]),
                    "ip": str(row[2])
                }
                break
        if contact:
            return contact
        else:
            return False


if __name__ == "__main__":
    active_threads = []
    keys = [] #keys[0] = clé de base, keys[1] = clé privée, keys[2] = clé publique, keys[3] = clé publique du contact pour l'import, keys[4] = clé publique du contact
    initialize(False)
    print("\nBienvenue Sur ETM ! (V. 1.0.0)\n")
    sleep(0.5)

    while True:
        user_choice = int(input("\n[?] Quel Est Votre Souhait ?\n\t1/ Héberger un salon ;\n\t2/ Me connecter à un salon ;\n\t3/ Modifier mes réglages ;\n\t4/ Afficher mes contacts ;\n\t5/ Ajouter un contact ;\n\t6/ Modifier mon statut ;\n\t7/ Afficher l'aide ;\n\t8/ C'est quoi ETM ? ;\n\t9/ Quitter ETM ;\n=> "))

        if user_choice == 1:
            choice = str(input("\n[?] Voulez-vous utiliser l'adresse IP enregistrée ? [O/N]\n=> "))
            if choice.lower() == "o":
                user_config = get_user_config()
                start_server(user_config["ip"])
            else:
                ip = str(input("\n[?] Quelle adresse IP voulez-vous utiliser ?\n=> "))
                start_server(ip)

        elif user_choice == 2:
            choice = int(input("\n[?] Voulez-vous vous connecter à un contact enregistré ou non enregistré ? [1/2]\n=> "))
            if choice == 1:
                name = str(input("\n[?] Quel est le nom de votre contact ?\n=> "))
                contact = getContactInfo(name)
                if contact != False:
                    start_client(contact["ip"])
                else:
                    print("\nVous n'avez aucun contact enregistré à ce nom !\n")
                    sleep(0.5)
            else:
                ip = str(input("\n[?] Quelle est l'adresse IP de votre contact ?\n=> "))
                start_client(ip)

        elif user_choice == 3:
            key = str(input("\n[?] Quelle clé voulez-vous modifier ? [description / name / ip]\n=> "))
            value = str(input("\n[?] Quelle nouvelle valeur voulez-vous attribuer à la clé {} ?\n=> ".format(key.lower())))
            modify_user_config(key, value)

        elif user_choice == 4:
            display_contacts()
            

        elif user_choice == 5:
            contact_name = str(input("\n[?] Quel est le nom de votre contact ?\n=> "))
            contact_description = str(input("\n[?] Quelle est la desription de votre contact ?\n=> "))
            contact_ip = str(input("\n[?] Quelle est l'adresse ip de votre contact.\n=> "))
            add_contact(contact_name, contact_description, contact_ip)


        elif user_choice == 6:
            choice = int(input("\n[?] Voulez-vous passer en mode en ligne ou en mode hors-ligne ? [1/2]\n=> "))
            modify_user_status(choice)

        elif user_choice == 7:
            print("\n[!] Bientôt\n")
            sleep(0.5)

        elif user_choice == 8:
            print("\n[!] Bientôt\n")
            sleep(0.5)

        elif user_choice == 9:
            modify_user_status(2)
            print("\n[!] Au revoir ! Appuyez sur une touche pour quitter.")
            sleep(0.5)
            break