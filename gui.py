# Import af moduler
import calendar
import datetime
import time
import tkinter
from tkinter import *
from tkinter.messagebox import askyesno

# Import af mine egne moduler
from dbHandler import dbHandler

# Initialiserer db
handler = dbHandler('examen.db')
# Laver databasestruktur
handler.makeStructure()
# Opret test-data i db - frisk testdata hver gang programmet startes
handler.insertDataset()



class Application(Frame):
    # lille funktion der sætter dato og klokkeslæt ind i GUI listen så vi kan se alderen på den viste data. Nyttigt ved
    # flerbruger applikationer der ikke har reservationshåndtering på data der bliver tilgået.
    # Dvs at brugeren selv må vurdere om det materiale han eller hun har kigget på i 2 timer stadig er ledigt for
    # udlån...
    def timestamp(self):
        timestamp = calendar.timegm(time.gmtime())
        human_readable = datetime.datetime.fromtimestamp(timestamp).isoformat()
        self.listGui.insert(INSERT, human_readable + '\n' + '\n')

    #  funktion der håndterer udlån af materialer
    def udlaan(self):
        # Fanger brugerens user_input fra tekstfeltet
        user_input = self.id_entry.get()
        # Her udlånes det korrekte materiale
        # Hvis der er user_input, kaldes metoden findesMateriale(user_input). returnerer materialeobjektet hvis det findes eller
        # None hvis det ikke gør.
        if user_input:
            materiale = handler.findesMateriale(user_input)
            if materiale:
                # test for materialets tilgængelighed
                # hvis ledigt
                if materiale.isAvailable():
                    handler.runSQL(materiale.toSQL('opskriv_udlaan'))
                    self.vis_hele_listen()
                # hvis ikke ledigt
                elif not materiale.isAvailable():
                    # dialog der giver brugeren mulighed for at reservere eller ikke
                    if askyesno('Hovsa', 'Alle eksemplarer er desværre udlånt - vil du reservere ?'):
                        tkinter.messagebox.showinfo('Udlån', f'Du har reserveret\n {materiale.titel}')
                        handler.runSQL(materiale.toSQL('opskriv_reservation'))
                        self.vis_hele_listen()
            else:
                # materiale ikke fundet
                tkinter.messagebox.showwarning('Udlån', 'Materiale eksisterer ikke!\nPrøv igen, eller kontakt '
                                                        'en administrator')
        else:
            # inputfelt tomt
            tkinter.messagebox.showerror('Udlån', 'Du skal indtaste i udlånsfeltet!')

    # Funktion der håndterer aflevering af materialer
    def aflever(self):
        # Fanger brugerens user_input fra tekstfeltet
        user_input = self.aflever_entry.get()
        # hvis der er input
        if user_input:
            # hent generér objekt fra database
            materiale = handler.findesMateriale(user_input)
            # hvis der er et objekt
            if materiale:
                # hvis der er udlånte eksemplarer
                if int(materiale.n_udlaan) > 0:
                    handler.runSQL(materiale.toSQL('nedskriv_udlaan'))
                    self.vis_hele_listen()
                # hvis der ikke er udlånte eksemplarer
                elif int(materiale.n_udlaan) == 0:
                    tkinter.messagebox.showwarning('Aflevering', 'Materialet er ikke udlånt!\nPrøv igen, eller kontakt '
                                                                 'en administrator')
            # hvis der ikke er et objekt
            else:
                tkinter.messagebox.showwarning('Aflevering', 'Materialet eksisterer ikke!\nPrøv igen, eller kontakt '
                                                             'en administrator')
        # hvis der ikke er et input
        else:
            tkinter.messagebox.showerror('Udlån', 'Du skal indtaste i afleveringsfeltet!')

    # Funktion der håndterer søgning i listMaterialer
    def sog_i_listen(self):
        user_input = self.entry.get()
        tabel_navne = ['BOG', 'FILM', 'CD', 'DRMLICENS']

        # Flag der sættes til True hvis materialet bliver fundet
        found = False

        # Iteration igennem toString() metoden for alle elementer i soegeliste. Jeg søger på enhver forekomst af
        # søgetesktsten i lowcase returværdien af funktionen.
        # hvis der er input
        if user_input:
            # linjen nedenunder sletter hele listen i GUI'en
            self.listGui.delete('1.0', END)
            self.timestamp()
            # for alle tabeller i databasen
            for tabel in tabel_navne:
                # hent liste med objekter fra tabel
                soegeliste = handler.makeObjects(tabel)
                # for alle materialer i listen med objekter
                for materiale in soegeliste:
                    # hvis der er et match i søgningen, sæt found til True og indsæt objektet i tekstfeltet listGui
                    if user_input.lower() in materiale.toString().lower():
                        found = True
                        self.listGui.insert(INSERT, materiale.toString() + '\n')
            # Hvis der ikke er match, prompt!
            if not found:
                self.listGui.insert(INSERT, 'Ingen resultater fundet, prøv igen!\n')
                tkinter.messagebox.showinfo('Søg i listen', 'Materialet findes ikke,\nprøv igen')
                # opdater listen igen
                self.vis_hele_listen()
        # hvis der ikke er input
        else:
            tkinter.messagebox.showerror('Søg i materialer', 'Din søgning er tom!')

    # Funktion der håndterer opdatering af tekstfeltet listGui.
    def vis_hele_listen(self):
        # linjen nedenunder sletter hele indholdet i tekstfeltet listGui
        self.listGui.delete('1.0', END)
        # Timestamp
        self.timestamp()
        # Indsæt alt materiale i listen fra databasen - lidt kluntet lavet, men det virker!
        for item in handler.makeObjects("BOG"):
            self.listGui.insert(INSERT, f'{item.toString()}\n')
        for item in handler.makeObjects("FILM"):
            self.listGui.insert(INSERT, f'{item.toString()}\n')
        for item in handler.makeObjects("CD"):
            self.listGui.insert(INSERT, f'{item.toString()}\n')
        for item in handler.makeObjects("DRMLICENS"):
            self.listGui.insert(INSERT, f'{item.toString()}\n')

    # funktion der håndterer sletning af materiale
    def slet_materiale(self):
        user_input = self.slet_entry.get()
        print(f"Materiale ID for sletning: {user_input}")
        # hvis der er input
        if user_input:
            # kald til handler.findesMateriale() returnerer None hvis der ikke findes et materiale med givet id.
            # Ellers returnerer det et objekt hvis der er et match på idnr i en af databasens tabeller
            materiale = handler.findesMateriale(user_input)
            # hvis der er et objekt
            if materiale:
                # hvis brugeren godkender sletning
                if askyesno("Sletning af materiale", f"Bekræft sletning af: {materiale.titel}"):
                    handler.runSQL(materiale.toSQL('slet'))
                    self.vis_hele_listen()
            # Hvis der ikke er objekt, prompt!
            else:
                self.listGui.insert(INSERT, 'Ingen resultater fundet, prøv igen!\n')
                tkinter.messagebox.showerror('Slet materiale', 'Ingen resultater fundet, prøv igen!')
        # hvis der ikke er input
        else:
            tkinter.messagebox.showerror('Slet materiale', 'Du skal indtaste i sletfeltet!')

    # Her initialiseres alle elementer i GUI
    def create_widgets(self):
        frame = Frame(self)
        frame2 = Frame(self)
        self.winfo_toplevel().title("Biblioteks databasen")

        # definition af quit knap
        self.QUIT = Button(frame, text="Afslut")
        self.QUIT["fg"] = "red"
        self.QUIT["command"] = self.quit
        self.QUIT.pack({"side": "left"})

        # definition og mapping af vis hele listen knappen.
        self.visListe = Button(frame, text="Vis hele listen")
        self.visListe["command"] = self.vis_hele_listen
        self.visListe.pack({"side": "left"})

        # definition af input søge feltet.
        self.L1 = Label(frame, text="Søge Streng")
        self.L1.pack(side=LEFT)
        self.entry = Entry(frame, bd=5)
        self.entry.pack(side=LEFT)

        # definition og mapping af søgeknappen.
        self.sogKnap = Button(frame, text="Søg i listen")
        self.sogKnap["command"] = self.sog_i_listen
        self.sogKnap.pack({"side": "left"})

        # definition af ID input feltet til udlån
        self.L1 = Label(frame, text="ID for udlån")
        self.L1.pack(side=LEFT)
        self.id_entry = Entry(frame, bd=5)
        # Burde virke, men virker ikke?
        # self.entry.bind('<Return>', self.sog_i_listen())
        self.id_entry.pack(side=LEFT)

        # definition af udlåns knappen og mapping til
        # en funktion.
        self.udlaanKnap = Button(frame, text="Udlån")
        self.udlaanKnap["command"] = self.udlaan
        self.udlaanKnap.pack({"side": "left"})

        # input felt til aflevering.
        self.L1 = Label(frame, text="ID for aflevering:")
        self.L1.pack(side=LEFT)
        self.aflever_entry = Entry(frame, bd=5)
        self.aflever_entry.pack(side=LEFT)

        # definition og mapping af afleveringsknap
        self.afleverKnap = Button(frame, text="Aflever")
        self.afleverKnap["command"] = self.aflever
        self.afleverKnap.pack({"side": "left"})

        # tilføjelse til udleveret GUI: et tekstfelt med tilhørende label og en knap med en slet funktion
        # definition af input feltet til slet, samt en knap til at teste min database ved at opdatere Text() listen
        # med data fra DB
        self.L1 = Label(frame2, text="ID for slet")
        self.L1.pack(side=LEFT)
        self.slet_entry = Entry(frame2, bd=5)
        self.slet_entry.pack(side=LEFT)

        # definition og mapping af slet knap
        self.sletKnap = Button(frame2, text="Slet materiale")
        self.sletKnap["command"] = self.slet_materiale
        self.sletKnap.pack(side=LEFT)

        # Her definerer vi en Text widget - dvs
        # den kan indeholde multiple linjer
        # ideen er så at hver linje indeholde et styk materiale
        # Nedenunder kan du se hvordan listen af materiale løbes
        # igennem og toString metoden bliver kaldt og så bliver
        # der indsat en ny linje i Text widgeten
        self.listGui = Text(self, width=140)

        frame.pack()
        frame2.pack()
        self.listGui.pack()

        # Opdatering af listGui
        # Timestamp der sætter etn dato og tid over den viste data
        self.timestamp()
        # Opdaterer listGUI med testdata
        self.vis_hele_listen()

    # Denne constructor køres når programmet starter
    # og sørger for at alle vores widgets bliver lavet.
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.create_widgets()


root = Tk()
app = Application(master=root)
app.mainloop()
