from sys import version_info, platform

version = version_info

if version[0] < 3:
    print("[X] ETM ne peut fonctionner correctement que sous python 3.0.0 minimum et votre version est actuellement la {}.{}.{} ; Veuillez mettre à jour python et réessayer.".format(str(version[0]), str(version[1]), str(version[2])))
else:

    from csv import writer, QUOTE_MINIMAL, reader
    from json import loads, dump
    import multiprocessing
    from os import system, path
    from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
    from threading import Thread
    from multiprocessing import Process
    from datetime import datetime
    from time import sleep

    print("\n[...] Vérification de l'installation des bibliothèques python...\n")
    sleep(0.25)

    try:
        print("\n[...] Vérification de l'installation de pycryptodome et pycryptodomex\n")
        sleep(0.25)
        from Cryptodome.PublicKey import RSA
        from Cryptodome.Cipher import PKCS1_OAEP
    except:
        print("\n[X] Pycryptodome et pycryptodomex ne sont pas installés !\n")
        sleep(0.25)
        system("pip3 install pycryptodome")
        system("pip3 install pycryptodomex")
        from Cryptodome.PublicKey import RSA
        from Cryptodome.Cipher import PKCS1_OAEP
    else:
        print("\n[!] Pycryptodome et pycryptodomex sont bien installés.\n")
        sleep(0.25)

    try:
        print("\n[...] Vérification de l'installation de termcolor...\n")
        sleep(0.25)
        from termcolor import colored
    except:
        print("\n[X] Termcolor n'est pas installé !\n")
        sleep(0.25)
        system("pip3 install termcolor")
        from termcolor import colored
    else:
        print("\n[!] Termcolor est bien installé !\n")
        sleep(0.25)

    try:
        print("\n[...] Vérification de l'installation de colorama...\n")
        sleep(0.25)
        from colorama import init
    except:
        print("\n[X] Colorama n'est pas installé !\n")
        sleep(0.25)
        system("pip3 install colorama")
        from colorama import init
        init()
    else:
        init()
        print("\n[!] Colorama est bien installé !\n")
        sleep(0.25)

    if platform == ("linux" or "linux2"):
        system("clear")
        print("\n[!] Sous linux, ETM doit être lancé en tant que sudo pour être certain de bien s'exécuter !")
    elif platform == ("win32" or "win64"):
        multiprocessing.set_start_method("spawn")
        system("cls")
    else:
        print("\nVous exécutez ETM depuis la plateforme [{}] qui n'est pas officiellement prise en charge par le logiciel (les plateformes prises en charge à 100% étant linux et windows). Les développeurs sont dans l'incapacité de vous garantir que le programme s'exécutera et fonctionnera correctement. L'équipe s'excuse d'avance pour la gêne occasionnée.\n".format(str(platform)))


    class thread(Thread):
        def __init__(self, ip, id, client_ip):
            Thread.__init__(self)
            self.ip = ip
            self.id = id
            self.client_ip = client_ip

        def run(self, connection:socket, server_error_code:int, client_ip:str):
            if server_error_code == 1:
                try:
                    connection.send(bytes("1", "utf-8"))
                    RSA_keys.append(connection.recv(16384))
                    connection.send(RSA_keys[2])
                    RSA_keys.append(PKCS1_OAEP.new(RSA.import_key(RSA_keys[3])))
                except ConnectionResetError:
                    pass          
                modify_cache("reset_cache")
                listener_process = Process(target=listener, args=(connection, self.client_ip, RSA_keys[0].export_key(),), daemon=True)
                listener_process.start()
                print("\n[+] Nouveau client connecté ({}:25115) ! Dès que vous voudrez quitter la discussion, entrez Exit.\n".format(client_ip))
                while True:
                    message = input("\n=> ")
                    modify_cache("save_message", "[{}] {}".format(str(self.ip), str(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))), message)
                    try:
                        connection.send(RSA_keys[4].encrypt(bytes(message, "utf-8")))
                    except ConnectionResetError:
                        pass
                    if message.lower() == "exit":
                        modify_cache("stop_listening")
                    if modify_cache("get_listening_status") == False:
                        user_choice = input("\n[?] Voulez-vous enregistrer cette conversation ? [O/N]\n=> ")
                        user_choice = verify_user_entry("str", user_choice, ["o", "n"], "[?] Voulez-vous enregistrer cette conversation ? [O/N]")
                        if user_choice.lower() == "o":
                            modify_cache("save_conversation")
                        break
                listener_process.terminate()                
                del(active_threads[int(self.id)])
                print("\n[!] Connexion fermée !\n")
                sleep(0.25)
            else:
                try:
                    connection.send(bytes("0", "utf-8"))
                except ConnectionResetError:
                    pass
                print("\n[X] Un client ({}:25115) a essayé de se connecter mais a été rejeté étant donné que vous êtes en mode hors-ligne. Utilisez l'option 3 du menu pour changer votre statut.\n".format(client_ip))
                sleep(0.25)


    def verify_user_entry(expected_type:str, value, desired_value:list, input_text:str):
        while True:
            try:
                value = eval("{}(value)".format(expected_type))
            except ValueError:
                print("\nVous avez entré une valeur de mauvais type ! Une valeur de type {} est attendue.\n".format(expected_type))
                sleep(1)
                value = input("\n{}\n=> ".format(input_text))
            else:
                if (type(value) == "str") and (len(desired_value) > 0):
                    value = value.lower()
                if (len(desired_value) > 0) and (value not in desired_value):
                    print("\nVous avez entré une mauvaise valeur ! Une valeur parmi les suivantes est attendue : {}. \n".format(desired_value))
                    sleep(1)
                    value = input("\n{}\n=> ".format(input_text))
                else:
                    break
        return value


    def modify_cache(request:str, key:str="", value:str=""):
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
            sleep(0.25)
        elif request == "save_message":
            with open("./cache.json", "r") as cache_file:
                JSONcontent = cache_file.read()
                cache_content = loads(JSONcontent)
                cache_file.close()
            cache_content["saved_conversation"][str(key)] = str(value)
            with open("./cache.json", "w") as cache_file:
                dump(cache_content, cache_file)
                cache_file.close()
        elif request == "save_conversation":
            with open("./cache.json", "r") as cache_file:
                JSON_cache_content = cache_file.read()
                cache_content = loads(JSON_cache_content)
                cache_file.close()
            if not path.exists("./saved_conversation.txt"):
                with open("./saved_conversation.txt", "x") as saved_conversation_file: saved_conversation_file.close()
            else:
                with open("./saved_conversation.txt", "w") as saved_conversation_file: saved_conversation_file.close()
            cache_content = cache_content["saved_conversation"].items()
            for elt in cache_content:
                with open("./saved_conversation.txt", "a") as saved_conversation_file:
                    saved_conversation_file.write("\n# {} =>".format(str(elt[0])))
                    saved_conversation_file.close()
                with open("./saved_conversation.txt", "a") as saved_conversation_file:
                    saved_conversation_file.write(str("\n\t\" {} \"\n".format(str(elt[1]))))
                    saved_conversation_file.close()
            if path.exists("./saved_conversation.txt"):
                print("\n[!] Conversation sauvegardée avec succès dans saved_conversation.txt !\n")
                sleep(0.25)
            else:
                print("\n[X] Échec lors de la sauvegarde de la conversation !\n")
                sleep(0.25)
        elif request == "stop_listening":
            with open("./cache.json", "r") as cache_file:
                JSON_cache_content = cache_file.read()
                cache_content = loads(JSON_cache_content)
                cache_file.close()
            cache_content["keep_listening"] = False
            with open("./cache.json", "w") as cache_file:
                dump(cache_content, cache_file)
                cache_file.close()
        elif request == "get_listening_status":
            with open("./cache.json", "r") as cache_file:
                JSON_cache_content = cache_file.read()
                cache_content = loads(JSON_cache_content)
                cache_file.close()
            return cache_content["keep_listening"]


    def initialize (force_user_config_regeneration:bool):
        print("[...] Génération de la clé RSA 4096 bits... Cette opération peut durer jusqu'à une trentaine de secondes suivant votre ordinateur.\n")
        RSA_keys.append(RSA.generate(4096))
        print("\n[!] La clé a été générée avec succès !\n")
        sleep(0.25)
        RSA_keys.append(" ")
        RSA_keys.append(RSA_keys[0].public_key().export_key())
        regenerate_user_config(force_user_config_regeneration)
        modify_user_status(1)
        modify_cache("reset_cache")


    def listener(s:socket, pair_ip:str, key:RSA.RsaKey):
        private_key = PKCS1_OAEP.new(RSA.import_key(key))
        while True:
            try:
                crypted_data = s.recv(16384)
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


    def start_server(ip:str):
        s = socket(AF_INET, SOCK_STREAM)
        s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        s.bind((str(ip), 25115))
        while True:
            s.listen(1)
            print("\n[!] Serveur démarré sur {}:25115. Si aucun client ne se connecte, quittez ETM et relancez-le pour revenir au menu.\n".format(str(ip)))
            sleep(1)
            connection, client_informations = s.accept()
            newthread = thread(ip, len(active_threads), client_informations[0])
            if get_user_config()["status"] == "offline":
                newthread.run(connection, 0, client_informations[0])
            else:
                active_threads.append(newthread)
                newthread.run(connection, 1, client_informations[0])
            if len(active_threads) <= 0:
                break
        for t in active_threads:
            t.start()


    def start_client(ip:str):
        message = ""
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((str(ip), 25115))
            server_error_code = s.recv(16384).decode("utf-8")
        except ConnectionRefusedError:
            print("\n[X] Connection à l'hôte impossible : l'hôte est hors-ligne ou indisponible.\n")
            sleep(0.25)
            s.close()
        else:
            if server_error_code == ("1"):
                s.send(RSA_keys[2])
                RSA_keys.append(s.recv(16384))
                RSA_keys.append(PKCS1_OAEP.new(RSA.import_key(RSA_keys[3])))
                print("\n[!] Connection à l'hôte réussie ! Dès que vous voudrez quitter la discussion, entrez Exit.\n")
                modify_cache("reset_cache")
                listener_process = Process(target=listener, args=(s, ip, RSA_keys[0].export_key(),), daemon=True)
                listener_process.start()
                while True:
                    message = input("\n=> ")
                    modify_cache("save_message", "[{}] {} ".format(str(ip), str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))), message)
                    try:
                        s.send(RSA_keys[4].encrypt(bytes(message, "utf-8")))
                    except ConnectionResetError:
                        pass
                    if message.lower() == "exit":
                        modify_cache("stop_listening")
                    if modify_cache("get_listening_status") == False:
                        user_choice = input("\n[?] Voulez-vous enregistrer cette conversation ? [O/N]\n=> ")
                        user_choice = verify_user_entry("str", user_choice, ["o", "n"], "[?] Voulez-vous enregistrer cette conversation ? [O/N]")
                        if user_choice.lower() == "o":
                            modify_cache("save_conversation")
                        break
                listener_process.terminate()
                s.close()
                print("\n[!] Connexion fermée !\n")
                sleep(0.25)
            else:
                print("\n[X] Connection à l'hôte impossible : l'hôte est hors-ligne ou indisponible.\n")
                sleep(0.25)
                s.close()


    def regenerate_user_config (force_regeneration:bool):
        if path.exists("./user.json") and force_regeneration == False:
            with open("./user.json", "r") as user_config_file:
                JSON_user_config_content = user_config_file.read()
                user_config_content = loads(JSON_user_config_content)
                try:
                    user_config_content["name"], user_config_content["description"], user_config_content["ip"], user_config_content["status"]
                except KeyError:
                    print("\n[X] Corruption du fichier de configuration détectée ! Le fichier a été régénéré. Désolé pour la gêne occasionnée.\n")
                    sleep(0.25)
                    regenerate_user_config(True)
                else:
                    if len(user_config_content) > 4:
                        print("\n[X] Corruption du fichier de configuration détectée ! Le fichier a été régénéré. Désolé pour la gêne occasionnée.\n")
                        sleep(0.25)
                        regenerate_user_config(True)
                    else:
                        pass
        else:
            if path.exists("./user.json"):
                with open("./user.json", "w") as user_config_file: user_config_file.close()
            else:
                with open("./user.json", "x") as user_config_file: user_config_file.close()
            user_config_file_template = {
                "name": "User",
                "description": "null",
                "ip": "127.0.0.1",
                "status": "online"
            }
            with open("./user.json", "w") as user_config_file:
                dump(user_config_file_template, user_config_file)
                user_config_file.close()
            print("\n[!] Nouveau fichier de configuration utilisateur généré. N'oubliez pas de jeter un coup d'oeil à vos paramètres pour les modifier.\n")
            sleep(0.25)


    def modify_user_config(key:str, value:str):
        if not path.exists("./user.json"):
            regenerate_user_config(False)
        with open("./user.json", "r") as user_config_file:
            JSON_user_config_content = user_config_file.read()
            user_config_content = loads(JSON_user_config_content)
            user_config_content[key] = value
            user_config_file.close()
        with open("./user.json", "w") as user_config_file:
            dump(user_config_content, user_config_file)
            user_config_file.close()
        print("\n[!] La valeur [{}] a été affectée à la clé [{}] avec succès !\n".format(value, key))
        sleep(0.25)


    def modify_user_status(user_choice:int=-1):
        if user_choice == -1:
            user_choice = input("\n[?] Voulez-vous être en ligne ou hors-ligne ? [1/2]\n=> ")
            user_choice = verify_user_entry("int", user_choice, [1, 2], "[?] Voulez-vous être en ligne ou hors-ligne ? [1/2]")
        if user_choice == 1:
            modify_user_config("status", "online")
        else:
            modify_user_config("status", "offline")
        print("\n[!] Statut modifié avec succès !\n")
        sleep(0.25)


    def get_user_config():
        with open("./user.json", "r") as user_config_file:
            JSON_user_config_content = user_config_file.read()
            user_config_content = loads(JSON_user_config_content)
            user_config_file.close()
            return user_config_content


    def add_contact (name:str, description:str, ip:str):
        if not path.exists("./contacts.csv"):
            with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
        with open("./contacts.csv", "a") as contacts_file:
            contacts_file_writer = writer(contacts_file, delimiter = " ", quotechar = "\"", quoting = QUOTE_MINIMAL)
            contacts_file_writer.writerow([str(name), str(description), str(ip)])
            contacts_file.close()
        print("\n[!] Contact crée avec succès !\n")
        sleep(0.25)


    def display_contacts():
        if not path.exists("./contacts.csv"):
            with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
        with open("./contacts.csv", "r") as contacts_file:
            contacts_file_reader = reader(contacts_file, delimiter=" ", quotechar = "\"")
            i = 1
            for row in contacts_file_reader:
                if len(row) > 0:
                    sleep(0.1)
                    print("\n[-] Contact numéro {}:\n\tNom: {}\n\tDescription: {}\n\tIP: {}\n".format(str(i), str(row[0]), str(row[1]), str(row[2])))
                    i = i + 1
                else:
                    print("\n")
            contacts_file.close()


    def getContactInfo(name:str):
        if not path.exists("./contacts.csv"):
            with open("./contacts.csv", "x") as contacts_file: contacts_file.close()
        with open("./contacts.csv", "r") as contacts_file:
            contacts_file_reader = reader(contacts_file, delimiter=" ", quotechar = "\"")
            for row in contacts_file_reader:
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


    def menu():
        logo = '''                   
    ███████╗████████╗███╗   ███╗
    ██╔════╝╚══██╔══╝████╗ ████║
    █████╗     ██║   ██╔████╔██║
    ██╔══╝     ██║   ██║╚██╔╝██║
    ███████╗   ██║   ██║ ╚═╝ ██║
    ╚══════╝   ╚═╝   ╚═╝     ╚═╝                                      
        '''

        print("\n{}\n\t(V. 1.0.2)\n".format(logo))

        if platform == ("linux" or "linux2"):
            system("clear")
        elif platform == ("win32" or "win64"):
            system("cls")

        while True:
            user_choice = input("\n[?] Quel Est Votre Souhait ?\n\t1/ Héberger un salon ;\n\t2/ Me connecter à un salon ;\n\t3/ Modifier mes réglages ;\n\t4/ Afficher mes contacts ;\n\t5/ Ajouter un contact ;\n\t6/ Modifier mon statut ;\n\t7/ Afficher l'aide ;\n\t8/ C'est quoi ETM ? ;\n\t9/ Quitter ETM ;\n\n=> ")
            user_choice = verify_user_entry("int", user_choice, [1,2,3,4,5,6,7,8,9], "[?] Quel Est Votre Souhait ?\n\t1/ Héberger un salon ;\n\t2/ Me connecter à un salon ;\n\t3/ Modifier mes réglages ;\n\t4/ Afficher mes contacts ;\n\t5/ Ajouter un contact ;\n\t6/ Modifier mon statut ;\n\t7/ Afficher l'aide ;\n\t8/ C'est quoi ETM ? ;\n\t9/ Quitter ETM ;\n")

            if user_choice == 1:
                user_choice = input("\n[?] Voulez-vous utiliser l'adresse IP enregistrée ? [O/N]\n=> ")
                user_choice = verify_user_entry("str", user_choice, ["o", "n"], "[?] Voulez-vous utiliser l'adresse IP enregistrée ? [O/N]")
                if user_choice.lower() == "o":
                    user_config = get_user_config()
                    start_server(user_config["ip"])
                else:
                    ip = input("\n[?] Quelle adresse IP voulez-vous utiliser ?\n=> ")
                    ip = verify_user_entry("str", ip, [], "[?] Quelle adresse IP voulez-vous utiliser ?")
                    start_server(ip)

            elif user_choice == 2:
                user_choice = input("\n[?] Voulez-vous vous connecter à un contact enregistré ou non enregistré ? [1/2]\n=> ")
                user_choice = verify_user_entry("int", user_choice, [1, 2], "[?] Voulez-vous vous connecter à un contact enregistré ou non enregistré ? [1/2]")
                if user_choice == 1:
                    name = input("\n[?] Quel est le nom de votre contact ?\n=> ")
                    name = verify_user_entry("str", name, [], "[?] Quel est le nom de votre contact ?")
                    contact = getContactInfo(name)
                    if contact != False:
                        start_client(contact["ip"])
                    else:
                        print("\nVous n'avez aucun contact enregistré à ce nom !\n")
                        sleep(0.25)
                else:
                    ip = input("\n[?] Quelle est l'adresse IP de votre contact ?\n=> ")
                    ip = verify_user_entry("str", ip, [], "[?] Quelle est l'adresse IP de votre contact ?")
                    start_client(ip)

            elif user_choice == 3:
                key = input("\n[?] Quelle clé voulez-vous modifier ? [description / name / ip]\n=> ")
                key = verify_user_entry("str", key, ["description","name","ip"], "[?] Quelle clé voulez-vous modifier ? [description / name / ip]")
                value = input("\n[?] Quelle nouvelle valeur voulez-vous attribuer à la clé {} ?\n=> ".format(key.lower()))
                value = verify_user_entry("str", value, [], str("[?] Quelle nouvelle valeur voulez-vous attribuer à la clé {} ?".format(key.lower())))
                modify_user_config(key, value)

            elif user_choice == 4:
                display_contacts()
                

            elif user_choice == 5:
                contact_name = input("\n[?] Quel est le nom de votre contact ?\n=> ")
                contact_name = verify_user_entry("str", contact_name, [], "[?] Quel est le nom de votre contact ?")
                contact_description = input("\n[?] Quelle est la desription de votre contact ?\n=> ")
                contact_description = verify_user_entry("str", contact_description, [], "[?] Quelle est la desription de votre contact ?")
                contact_ip = input("\n[?] Quelle est l'adresse ip de votre contact ?\n=> ")
                contact_ip = verify_user_entry("str", contact_ip, [], "[?] Quelle est l'adresse ip de votre contact ?")
                add_contact(contact_name, contact_description, contact_ip)


            elif user_choice == 6:
                user_choice = input("\n[?] Voulez-vous passer en mode en ligne ou en mode hors-ligne ? [1/2]\n=> ")
                user_choice = verify_user_entry("int", user_choice, [1,2], "[?] Voulez-vous passer en mode en ligne ou en mode hors-ligne ? [1/2]")
                modify_user_status(user_choice)

            elif user_choice == 7:
                print("\n[!] Bientôt\n")
                sleep(0.25)

            elif user_choice == 8:
                print("\n[!] Bientôt\n")
                sleep(0.25)

            elif user_choice == 9:
                modify_user_status(2)
                print("\n[!] Au revoir !")
                sleep(1)
                break


    if __name__ == "__main__":
        active_threads = []
        RSA_keys = [] #RSA_keys[0] = clé de base, RSA_keys[1] = clé privée, RSA_keys[2] = clé publique, RSA_keys[3] = clé publique du contact pour l'import, RSA_keys[4] = clé publique du contact
        initialize(False)

        sleep(0.25)

        daemon = Process(target=menu(), daemon=True)
        daemon.start()

# By XWaz \(°o°)/