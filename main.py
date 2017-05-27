#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import urllib
import os
import kivy
kivy.require("1.9.0")

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from functools import partial
from random import randint
from BeautifulSoup import BeautifulSoup


class Control:
    """Klasa odpowiedzialna za mechanikę aplikacji."""
    def __init__(self):
        self.glowna = "http://xkcd.com/"
        self.aktywna = "http://xkcd.com/"
        self.max_numer = self.komiks_info(self.glowna)["numer"]

    @staticmethod
    def komiks_info(adres):
        """Metoda zwracająca inforamcję o komiksie.

        Argumenty:
            adres (str):    Adres strony komiksu, o którym mają zostać zwrócone informacje.

        Zwraca:
            Słownik, gdzie: element o kluczu "url" to adres pod którym znajduje się plik graficzny przedstawiający komiks, "nazwa_img" -
            nazwa tego pliku, a "numer" - numer komiksu.
        """
        soup = BeautifulSoup(urllib.urlopen(adres))
        numer = soup.findAll(rel="prev")[0]["href"]

        # Jeśli z danego komiksu nie da się przejść do poprzedniego, to jest on pierwszym komiksem
        if numer == "#":
            numer = "1"
        else:
            numer = str(int(numer.split('/')[1]) + 1)

        url = "http:" + soup.findAll(id="comic")[0].img["src"]
        return {"url": url, "nazwa_komiksu": soup.findAll(id="ctitle")[0].text, "nazwa_img": url.split('/')[-1], "numer": numer}

    def wczytaj_komiks(self, nav, strona):
        """Metoda pobiera plik graficzny przedstawiający komiks, oraz aktualizuje dane.

        Argumenty:
            strona (str):   Numer strony, która ma zostać wczytana, jeśli nav = "entry".
            nav (str):      Ciąg znaków mówiący o tym, który komiks ma zostać wczytany. "entry" oznacza, że ma być wczytany komiks o numerze
                            podanym przez użytkownika, "next" - następny komiks w stosunku do bieżącego, "prev" - porzedni komiks w stosunku
                            do bieżącego, "rand" - losowy komiks. W przypadku, kiedy nie zostanie podany ciąg znaków lub będzie nie będzie
                            on jednym z wyżej wymienionych, to zostanie wczytany komiks znajdujący się na stronie głównej.

        Zwraca:
            Słownik, gdzie: klucz "tytul" to tytuł komiksu, "obraz" - ścieżka pod którą znajduje się pobrany plik przedstawiający komiks,
            "nr_komiksu" - numer strony pod którą znajduje się komiks.
        """
        adres = self.glowna

        try:
            aktywny_info = self.komiks_info(self.aktywna)

            if nav == "entry":
                adres += strona
            elif nav == "next":
                adres += str(int(aktywny_info["numer"]) + 1)
            elif nav == "prev":
                adres += str(int(aktywny_info["numer"]) - 1)
            elif nav == "rand":
                adres += str(randint(1, int(self.max_numer)))

            nowy_info = self.komiks_info(adres)

            # Jeśli katalog cache nie istnieje, to go utwórz
            if not os.path.exists("cache"):
                os.mkdir("cache")

            # Jeśli komiks nie znajduje się w katalogu cache to pobierz go ze strony
            if not os.path.exists("cache/" + nowy_info["nazwa_img"]):
                urllib.urlretrieve(nowy_info["url"], "cache/" + nowy_info["nazwa_img"])

            self.aktywna = adres

            return {"tytul": "[b]{}[/b]".format(nowy_info["nazwa_komiksu"]),
                    "obraz": "cache/" + nowy_info["nazwa_img"],
                    "nr_komiksu": nowy_info["numer"]}

        except IndexError:
            return False


class GUI(BoxLayout):
    """Klasa odpowiedzialna za graficzny interfejs użytkownika aplikacji."""
    def __init__(self, **kwargs):
        """Metoda inicjalizująca obiekt klasy GUI.

        Metoda tworzy układ na którym umieszczany jest tytuł, obrazek, przyciski odpowiadające za: losowanie, przejście do poprzedniego
        obrazka, przejście do następnego obrazka, oraz przejście do najnowszego obrazka, a także pole tekstowe służące do wpisywania numeru
        obrazka do którego użytkownik chce przejść.
        """
        super(GUI, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.rows = 4
        self.tytul = Label(text="Hello World!", size_hint=(1, .15), markup=True)
        self.label_strona = Label(text="Strona: ")
        self.btn_najnowszy = Button(text=">|")
        self.btn_nastepny = Button(text=">")
        self.btn_poprzedni = Button(text="<")
        self.btn_losuj = Button(text="Losuj")
        self.btn_przejdz = Button(text="Przejdź")
        self.nr_komiksu = TextInput(multiline=False)
        self.view = ScrollView()
        self.obrazek = Image(size_hint=(None, None), keep_ratio=True)
        self.obrazek.size = self.obrazek.texture_size
        self.hbox1 = BoxLayout(orientation="horizontal", size_hint=(1, .15))
        self.hbox2 = BoxLayout(orientation="horizontal", size_hint=(1, .1))
        self.control = Control()

        # Rozmieszczanie widgetów
        self.hbox1.add_widget(self.btn_losuj)
        self.hbox1.add_widget(self.btn_poprzedni)
        self.hbox1.add_widget(self.btn_nastepny)
        self.hbox1.add_widget(self.btn_najnowszy)
        self.hbox2.add_widget(self.label_strona)
        self.hbox2.add_widget(self.nr_komiksu)
        self.hbox2.add_widget(self.btn_przejdz)
        self.add_widget(self.tytul)
        self.view.add_widget(self.obrazek)
        self.add_widget(self.view)
        self.add_widget(self.hbox1)
        self.add_widget(self.hbox2)

        # Podłączanie kontrolek pod metodę
        self.btn_losuj.bind(on_press=partial(self.akcja, "rand"))
        self.btn_nastepny.bind(on_press=partial(self.akcja, "next"))
        self.btn_poprzedni.bind(on_press=partial(self.akcja, "prev"))
        self.btn_najnowszy.bind(on_press=partial(self.akcja, "main"))
        self.nr_komiksu.bind(on_text_validate=partial(self.akcja, "entry"))
        self.btn_przejdz.bind(on_press=partial(self.akcja, "entry"))

        self.akcja(Window, "main")  # Wczytanie strony głównej podczas startu aplikacji

    def akcja(self, nav, widget):
        """Metoda ustawia odpowiedni tytuł komiksu, reprezentujący go obrazek, oraz numer strony na której się on znajduje.

            Argumenty:
                nav (str):                  Ciąg znaków mówiący o tym, który komiks ma zostać ustawiony. "entry" oznacza, że ma zostać
                                            ustawiony komiks o numerze podanym przez użytkownika, "next" - następny komiks w stosunku do
                                            bieżącego, "prev" - porzedni komiks w stosunku do bieżącego, "rand" - losowy komiks.
                widget (kivy.uix.widget):   Widget odpowiedzialny za wywołanie tej metody (potrzebny tylko do wywołania metody).
        """
        del widget
        strona = self.nr_komiksu.text
        wynik = self.control.wczytaj_komiks(nav, strona)

        if wynik:
            # Aktualizacja GUI
            self.tytul.text = wynik["tytul"]
            self.nr_komiksu.text = wynik["nr_komiksu"]
            self.obrazek.source = wynik["obraz"]
            self.obrazek.size = Window.size
            self.obrazek.reload()
        else:
            self.tytul.text = '[color=ff0000][b]Wystąpił błąd podczas wczytywania komiksu![/b]'


class Application(App):
    """Główna klasa aplikacji."""
    def build(self):
        """Nadpisanie metody, powodujące wyświetlenie układu GUI na głównym oknie aplikacji."""
        return GUI()


if __name__ == "__main__":
    Application().run()
