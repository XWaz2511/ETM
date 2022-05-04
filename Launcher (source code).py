from sys import version_info, platform, exit
from os import system
from time import sleep
import subprocess

version = version_info

def pause_program():
    wait = input("\nVeuillez appuyer sur une touche pour continuer...\n")


logo = '''
    ███████╗████████╗███╗   ███╗
    ██╔════╝╚══██╔══╝████╗ ████║
    █████╗     ██║   ██╔████╔██║
    ██╔══╝     ██║   ██║╚██╔╝██║
    ███████╗   ██║   ██║ ╚═╝ ██║
    ╚══════╝   ╚═╝   ╚═╝     ╚═╝
        '''

print(str("\n{}\n\t(V. 1.2.3)\n".format(logo)))

relaunch = False

if version[0] < 3:
    print("[X] ETM ne peut fonctionner correctement que sous python 3.0.0 minimum et votre version est actuellement la {}.{}.{} ; Veuillez mettre à jour python et réessayer.".format(str(version[0]), str(version[1]), str(version[2])))
    pause_program()
    exit()
else:
    print("\nVérification de l'installation des dépendances...\n")
    sleep(0.5)
    try:
        from Cryptodome.PublicKey import RSA
        from Cryptodome.Cipher import PKCS1_OAEP
    except:
        print("\n[X] Pycryptodome et pycryptodomex ne sont pas installés !\n")
        system("pip install pycryptodome")
        system("pip install pycryptodomex")
        relaunch = True
    else:
        print("\nPycryptodome et pycryptodomex sont bien installés !\n")

    try:
        from termcolor import colored
    except:
        print("\n[X] Termcolor n'est pas installé !\n")
        system("pip install termcolor")
        relaunch = True
    else:
        print("\nTermcolor est bien installé !\n")

    try:
        from colorama import init
    except:
        print("\n[X] Colorama n'est pas installé !\n")
        system("pip install colorama")
        relaunch = True
    else:
        print("\nColorama est bien installé !\n")

    if relaunch:
        print("\n[!] Les bibliothèques python manquantes ont été installées. Veuillez relancer ETM pour finaliser l'installation.\n")
        pause_program()
        exit()
    else:
        if platform == ("linux" or "linux2"):
            print(colored("\n[!] Sous linux, ETM doit être lancé en tant que sudo pour être certain de bien s'exécuter !\n", "blue"))
            pause_program()
            subprocess.call("python ./bin/ETM.py", shell=True)
        elif platform == ("win32" or "win64"):
            pause_program()
            subprocess.call("python ./bin/ETM.py", shell=True)
        else:
            print("\nVous exécutez ETM depuis la plateforme [{}] qui n'est pas officiellement prise en charge par le logiciel (les plateformes prises en charge à 100% étant linux et windows). Les développeurs sont dans l'incapacité de vous garantir que le programme s'exécutera et fonctionnera correctement. L'équipe s'excuse d'avance pour la gêne occasionnée.\n".format(str(platform)))