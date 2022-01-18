import csv
import json
import datetime
import os

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


def write_message (message, author, room):
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


def update_contacts_status():


def modify_contact():


if __name__ == "__main__":
    initialize(False)
    print("Bienvenue Sur EMT. Quel Est Votre Souhait ?\n\t1/ Me connecter à un salon;\n\t2/ Héberger un salon;\n\t3/ Modifier mes réglages;\n\t4/ Afficher mes contacts;\n\t5/ Ajouter un contact;\n\t6/ Modifier mon statut;\n\t7/ Afficher l'aide;\n\t8/ C'est quoi ETM ?;")

    #write_message("ezafaze","azef", "test")
    #read_messages("test")