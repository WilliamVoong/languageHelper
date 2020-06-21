import tkinter as tk
from tkinter import ttk
from googletrans import Translator
import requests
from bs4 import BeautifulSoup
import config
import os

# detect the current working directory and print it
path = os.getcwd()
os.chdir("C:/Users/lewiv/PycharmProjects/languageHelper")



class TextObservable:
    text = ""
    listeners = []

    def __init__(self):
        self.listeners = []

    def addListener(self, tobject):
        self.listeners.append(tobject)

    def notifyListeners(self):
        for listener in self.listeners:
            listener.notify(self.text)

    def setText(self, text):
        if self.text != text:
            self.text = text
            self.notifyListeners()


class ClipboardTextListener:
    window = None
    text = ""

    def __init__(self, window):
        self.window = window

    def notify(self, text):
        self.text = text

    def copyToClipboard(self):
        window.clipboard_clear()
        window.clipboard_append(self.text)


class FileForm:
    def __init__(self, path):
        self.path = path
        self.dic = {}

    def read(self):
        with open(self.path, 'r') as reader:
            for word in reader:
                word.strip()
                l = word.split()
                self.dic.update({l[0]: int(l[1])})
        return self.dic


class WordFormDisplay:
    arr = []
    wordForm = None
    language = ""
    window = None

    def __init__(self, window, wordForm, language):
        self.wordForm = wordForm
        self.language = language
        self.window = window

    def display(self):
        for label in self.arr:
            label.grid_forget()
        i = 40
        print(self.language)
        for word in self.wordForm:
            trans = Translator()

            headerLabel = tk.Label(self.window,
                                    text=word + "  (" + trans.translate(word, src=config.config["SETTINGS"]["LanguageToLearn"], dest=self.language).text + ")",bg=config.config["Color"]["bg"])
            headerLabel.grid(column=2, row=i, sticky="E")
            contentLabel = tk.Label(self.window, text=self.wordForm[word], bg=config.config["Color"]["bg"])
            contentLabel.grid(column=3, row=i, sticky="E")
            self.window.columnconfigure(0, minsize=10)
            self.window.columnconfigure(1, minsize=10)
            self.arr.append(contentLabel)
            self.arr.append(headerLabel)
            i += 1




class AbstractWordFinder:
    def __init__(self, word, textfile, url):
        self.word = word
        self.textfile = textfile
        self.url = url

    def findWords(self):
        htmlScraper = HtmlScraper(self.url, self.word)
        soup = htmlScraper.scrapeResults()
        w = FileForm("wordForms\\" + self.textfile)
        w = w.read()
        return self.processWords(soup, w)

    def processWords(self, soup, words):
        pass


class PronounFinder(AbstractWordFinder):
    def processWords(self, soup, words):
        dic = {}
        for link in soup.find_all('tr')[1:]:
            substring = link.get_text().split()
            for x in words:
                if x == substring[0]:
                    try:
                        dic.update({"singular": ' '.join(substring[1:1 + words[x]])})
                    except IndexError:
                        pass
                    try:
                        dic.update({"plural": substring[2 + words[x]]})
                    except IndexError:
                        pass
        return dic


class VerbFinder(AbstractWordFinder):
    def processWords(self, soup, words):
        dic = {}
        for link in soup.find_all('tr')[1:]:
            substring = link.get_text().split()
            for x in words:

                if x == substring[0]:
                    try:
                        dic.update({x: ' '.join(substring[1:1 + words[x]])})
                    except: pass
        return dic


class AdjectiveFinder(AbstractWordFinder):
    def processWords(self, soup, words):
        dic = {}
        for link in soup.find_all('tr')[1:]:
            substring = link.get_text().split()
            for x in words:
                if x == substring[0]:
                    try:
                        dic.update({x: ' '.join(substring[1:1 + words[x]])})
                    except IndexError:
                        pass
        return dic


# HtmlScraper the purpose is to use this tool to scrape webpages for information
class HtmlScraper:

    # url  -> the standard url for the website to webscrape from
    # word -> the word to append to then end of the url
    # example -> if úrl = www.xxx.com/, and  word = example, then self.url= www.xxx.com/example
    #           would be the adress processed 
    def __init__(self, url, word):
        self.url = url + word

    # scrapes content from the given url
    # and returns a soup object for that website
    def scrapeResults(self):
        r = requests.get(self.url)
        html_doc = r.text
        return BeautifulSoup(html_doc, 'html.parser')

def updateWordOnScreen(event, textObservable):
        notEmptyText = len(nameEntered.get("1.0", "end").strip()) != 0
        if notEmptyText:
            language = translator.detect(nameEntered.get("1.0", "end")).lang
            translatedWordForm = None
            isNotLanguageToLearn= not config.config["SETTINGS"]["LanguageToLearn"] in language
            if isNotLanguageToLearn:
                translatedWord = translator.translate(nameEntered.get("1.0", "end"),
                                                      src=config.config["SETTINGS"]["UserLanguage"],
                                                      dest=config.config["SETTINGS"]["LanguageToLearn"]).text
                firstphrase = translator.translate('ordet är ', dest=language).text
                label.configure(text=firstphrase + " : \n" + translatedWord)
                translatedWordForm = findRelatedWords(translatedWord)
            else:


                language = config.config["SETTINGS"]["UserLanguage"]
                firstphrase = translator.translate('ordet är ',src=config.config["SETTINGS"]["LanguageToLearn"],  dest=config.config["SETTINGS"]["UserLanguage"]).text
                print(firstphrase)
                translatedWord = translator.translate(nameEntered.get("1.0", "end"),
                                                      src=config.config["SETTINGS"]["LanguageToLearn"],
                                                      dest=config.config["SETTINGS"]["UserLanguage"]).text
                label.configure(text=firstphrase + " : \n " + translatedWord)
                translatedWordForm = findRelatedWords(translator.translate(nameEntered.get("1.0", "end"),
                                                                           dest=config.config["SETTINGS"][
                                                                               "LanguageToLearn"]).text)
            WordFormDisplay(window, translatedWordForm, language).display()
            textObservable.setText(translatedWord)

class WordFinderCollection():
    def __init__(self):
        self.dic= {}
    def add(self,abstractWordFinder):
        self.dic.update(abstractWordFinder.findWords())

def findRelatedWords(word):
    wordfinder = WordFinderCollection()
    wordfinder.add(AdjectiveFinder(word, "adjectiveForm.txt", "https://www.synonymer.se/sv-syn/"))
    wordfinder.add(VerbFinder(word, "verbForms.txt", "https://www.synonymer.se/sv-syn/"))
    wordfinder.add(PronounFinder(word, "nounforms.txt", "https://www.synonymer.se/sv-syn/"))
    return wordfinder.dic


window = tk.Tk()
window.configure(bg=config.config["Color"]["bg"])
window.title('LanguageHelper')
photo=tk.PhotoImage(file="button.png")
photo= photo.subsample(3,3)
window.minsize(600, 430)
translator = Translator()
window.grid_propagate(False)
nameEntered = tk.Text(window, width=30, height=15)
nameEntered.grid(column=2, row=0, pady=(10, 25), padx=(25, 0), columnspan=4)
frame= tk.Frame( window,width=250,height=245,borderwidth = 1,highlightbackground="black",highlightthickness=1)
frame.grid(column=0, row=0,columnspan=2,sticky="N", pady=(10),padx=20)
frame.pack_propagate(0)
label = ttk.Text(frame, text=" Enter the word to be translated ",wraplengt=200, width=23)
label.pack()
label.config(font=("Georgia", 13))

#label.grid(column=0, row=0, sticky="N", padx=(40, 20), columnspan=2,pady=(10))
clipboard = ClipboardTextListener(window)
textObservable = TextObservable()
textObservable.addListener(clipboard)
clipboardButton = ttk.Button(window, text="Copy to ClipBoard",image=photo, command=clipboard.copyToClipboard, width=30)
clipboardButton.grid(row=40, column=1, padx=(0, 30), sticky="NW",rowspan=3)


window.bind('<Return>', lambda event: updateWordOnScreen(event, textObservable))
window.mainloop()




