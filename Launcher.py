from sys import platform
from os import system


def pause_program():
    wait = input("\nVeuillez appuyer sur une touche pour continuer...\n")


if platform == ("linux" or "linux2"):
    system("sudo python ./ETM.py")
elif platform == ("win32" or "win64"):
    system("python ./ETM.py")
else:
    print("Votre plateforme ne peut pas exécuter ETM !")
    pause_program()
