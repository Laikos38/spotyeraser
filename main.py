from utils.enums import Menu
from utils.spotipy_handler import SpotipyHandler
from platform import system
from os import system as sys_command
from threading import Thread
from time import sleep
from queue import Queue

class Main:
    def __init__(self):
        self.menu = Menu.LOGIN
        self.exit = False
        self.spotipyHandler = None

    def print_logo(self):
        self.clscreen()
        logo = "█▀ █▀█ █▀█ ▀█▀ █▄█   █▀▀ █▀█ ▄▀█ █▀ █▀▀ █▀█\n" + \
               "▄█ █▀▀ █▄█ ░█░ ░█░   ██▄ █▀▄ █▀█ ▄█ ██▄ █▀▄\n"
        print(logo)

    def print_menu(self):
        if self.menu == Menu.LOGIN:
            print("1- Authorize Spotify.\n"
                  "2- Login with previously used account .\n"
                  "q- Exit.\n>>> ", end="")
        elif self.menu == Menu.MAIN:
            print("1- Erase liked songs.\n"
                  "2- Erase followed artists.\n"
                  "3- Erase saved albums.\n"
                  "4- Erase saved shows/podcasts.\n"
                  "5- Erase all.\n"
                  "q- Exit.\n>>> ", end="")

    def execute_option(self):
        option = input()
        if self.menu == Menu.LOGIN:
            if option == "1":
                self.auth(False)
            elif option == "2":
                self.auth(True)
            elif option == "q":
                self.exit = True
            else:
                print("ERROR. Invalid option.")
                self.screen_pause()
        elif self.menu == Menu.MAIN:
            if option == "q":
                self.exit = True
            elif option == "1":
                self.erase_tracks()
                self.screen_pause()
            elif option == "2":
                self.erase_artists()
                self.screen_pause()
            elif option == "3":
                self.erase_albums()
                self.screen_pause()
            elif option == "4":
                self.erase_shows()
                self.screen_pause()
            elif option == "5":
                self.erase_all()
                self.screen_pause()
            else:
                print("ERROR. Invalid option.")
                self.screen_pause()

    def erase_tracks(self, warning=True):
        if warning:
            msg = "This action will delete all your liked songs, are you sure you wanna continue?\n"\
                  "1- Yes, delete all this crap.\n"\
                  "2- No, I change my mind.\n"\
                  ">>> "
            if self.yes_no_warning(msg) == "2":
                return
                
        result = Queue()
        t = Thread(target=self.spotipyHandler.erase_user_saved_tracks, args=[result])
        t.start()
        self.clscreen()
        print("Erasing tracks", end="")
        while t.is_alive():
            print(".", end="")
            sleep(1)
        result = result.get()
        self.clscreen()
        if result:
            print("Tracks erased successfully!")
        else:
            print("An error occurred during the erase process :(")

    def erase_artists(self, warning=True):
        if warning:
            msg = "This action will unfollow all your followed artists, are you sure you wanna continue?\n"\
                  "1- Yes, nobody wants to follow Nickelback.\n"\
                  "2- No, I change my mind, I love Nickelback.\n"\
                  ">>> "
            if self.yes_no_warning(msg) == "2":
                return

        result = Queue()
        t = Thread(target=self.spotipyHandler.erase_user_saved_artists, args=[result])
        t.start()
        self.clscreen()
        print("Erasing artists", end="")
        while t.is_alive():
            print(".", end="")
            sleep(1)
        result = result.get()
        self.clscreen()
        if result:
            print("Artists erased successfully!")
        else:
            print("An error occurred during the erase process :(")

    def erase_albums(self, warning=True):
        if warning:
            msg = "This action will delete all your liked albums, are you sure you wanna continue?\n"\
                  "1- Yes, delete all this crap.\n"\
                  "2- No, I change my mind.\n"\
                  ">>> "
            if self.yes_no_warning(msg) == "2":
                return
        result = Queue()
        t = Thread(target=self.spotipyHandler.erase_user_saved_albums, args=[result])
        t.start()
        self.clscreen()
        print("Erasing albums", end="")
        while t.is_alive():
            print(".", end="")
            sleep(1)
        result = result.get()
        self.clscreen()
        if result:
            print("Albums erased successfully!")
        else:
            print("An error occurred during the erase process :(")

    def erase_shows(self, warning=True):
        if warning:
            msg = "This action will delete all your liked shows/podcasts, are you sure you wanna continue?\n"\
                  "1- Yes, delete all this crap.\n"\
                  "2- No, I change my mind.\n"\
                  ">>> "
            if self.yes_no_warning(msg) == "2":
                return
        result = Queue()
        t = Thread(target=self.spotipyHandler.erase_user_saved_shows, args=[result])
        t.start()
        self.clscreen()
        print("Erasing shows/podcasts", end="")
        while t.is_alive():
            print(".", end="")
            sleep(1)
        result = result.get()
        self.clscreen()
        if result:
            print("Shows/Podcasts erased successfully!")
        else:
            print("An error occurred during the erase process :(")

    def erase_all(self):
        self.clscreen()
        msg = "This action will delete all your liked songs, albums, shows/podcasts and unfollow your followed artists.\n"\
                "Are you sure you wanna continue?\n"\
                "1- Yes, delete all this crap.\n"\
                "2- No, I change my mind.\n"\
                ">>> "
        if self.yes_no_warning(msg) == "2":
            return
        self.clscreen()
        self.erase_tracks(warning=False)
        self.erase_albums(warning=False)
        self.erase_shows(warning=False)
        self.erase_artists(warning=False)
        self.clscreen()
        print("\nDone! Hope you enjoy you clean spotify!")

    def yes_no_warning(self, msg):
        confirmation = ""
        while confirmation != "1" and confirmation != "2":
            self.clscreen()
            print(msg, end="")
            confirmation = input()
            if confirmation != "1" and confirmation != "2":
                print("ERROR. Invalid option.")
                self.screen_pause()
        return confirmation

    def auth(self, cached=False):
        self.clscreen()
        try:
            self.spotipyHandler = SpotipyHandler()
            if self.spotipyHandler.login(cached=cached):
                self.menu = Menu.MAIN
                self.clscreen()
                print("Login successful!\n")
        except:
            self.clscreen()
            print("ERROR during login process.\n")
        self.screen_pause()

    def screen_pause(self):
        input("\n\nPress ENTER key to continue...")

    def clscreen(self):
        if system() == "Windows":
            sys_command("cls")
        elif system() == "Linux":
            sys_command("clear")
        elif system() == "Darwin":
            sys_command("clear")
        else:
            print("\n" * 20)

    def run(self):
        while not self.exit:
            self.print_logo()
            self.print_menu()
            self.execute_option()
        print("\nbye!")

if __name__ == '__main__':
    main = Main()
    main.run()