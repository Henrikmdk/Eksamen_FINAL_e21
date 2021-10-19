# Klasse der indeholder attributter og metoder til håndtering af database.
# Jeg har ikke kigget nærmere på typisk design mønster for impementering af databaser, men denne klasse lader til at
# virke som den skal og gøre min kode genbrugelig
# Dens formål er at lære sqlite3 og lidt SQL. Klassen opretter en  databasefil der hedder 'examen.db'.
# Der er ligeledes funktioner der kan lave objekter af typen Bog, Film, CD og DRMLicens fra data i databasen.
# jeg returnerer en liste med et objekt i makeObject() og en liste med flere objekter i makeObjects()

# Imports
import sqlite3
from klasser import Bog, Film, CD, DRMLicens


class dbHandler:
    # constructor der laver en database hvis den ikke findes i forvejen og initiliserer en cursor.
    def __init__(self, dbNavn):
        self.dbNavn = dbNavn
        # Skaber forbindelse til databasen. Hvis den ikke eksisterer, bliver den oprettet
        self.conn = sqlite3.connect(self.dbNavn)
        self.cursor = self.conn.cursor()
        self.dataset = []

    # metode der laver database strukturen. Tabellerne afspejler mine klasser i klasser.py
    def makeStructure(self):
        # Sletter tabeller i databasen så jeg har en tom database at arbejde med til testdataen
        self.cleanDB()

        # opretter tabel BOG
        self.cursor.execute('''CREATE TABLE BOG
                            (ID INTEGER PRIMARY KEY NOT NULL,
                            TITEL TEXT NOT NULL,
                            ANTAL TEXT NOT NULL,
                            N_UDLAAN TEXT NOT NULL,
                            RESERVEREDE TEXT NOT NULL,
                            AARSTAL TEXT NOT NULL,
                            N_SIDER TEXT NOT NULL,
                            FORFATTER TEXT NOT NULL)''')
        # opretter tabel FILM
        self.cursor.execute('''CREATE TABLE FILM
                            (ID INTEGER PRIMARY KEY NOT NULL,
                            TITEL TEXT NOT NULL,
                            ANTAL TEXT NOT NULL,
                            N_UDLAAN TEXT NOT NULL,
                            RESERVEREDE TEXT NOT NULL,
                            AARSTAL TEXT NOT NULL,
                            INSTRUKTOER TEXT NOT NULL,
                            VARIGHED TEXT NOT NULL)''')
        # opretter tabel CD
        self.cursor.execute('''CREATE TABLE CD
                            (ID INTEGER PRIMARY KEY NOT NULL,
                            TITEL TEXT NOT NULL,
                            ANTAL TEXT NOT NULL,
                            N_UDLAAN TEXT NOT NULL,
                            RESERVEREDE TEXT NOT NULL,
                            AARSTAL TEXT NOT NULL,
                            KUNSTNER TEXT NOT NULL,
                            TRACKS TEXT NOT NULL,
                            TOTAL_VARIGHED TEXT NOT NULL)''')
        # opretter tabel DRMLICENS
        self.cursor.execute('''CREATE TABLE DRMLICENS
                            (ID INTEGER PRIMARY KEY NOT NULL,
                            TITEL TEXT NOT NULL,
                            ANTAL TEXT NOT NULL,
                            N_UDLAAN TEXT NOT NULL,
                            RESERVEREDE TEXT NOT NULL,
                            AARSTAL TEXT NOT NULL,
                            SKABER TEXT NOT NULL,
                            FORMATTYPE TEXT NOT NULL,
                            TIDSBEGRAENSNING TEXT NOT NULL)''')
        self.statusEcho('Tabellerne Materialer, Bog, Film, CD og DRMLicens er oprettet')
        # commit SQL i databasen
        self.conn.commit()

    # metode jeg bruger til at insætte mine data i databsen
    def insertDataset(self):
        # Testdata - objekter instansieret direkte i en liste
        self.dataset = [Bog(1, 'The Silver Spoon', 10, 3, 0, 2011, 1505, 'Il Cucchiaio d’Argento'),
                          Bog(2, 'The Fat Duck Cookbook', 2, 2, 12, 2009, 532, 'Heston Blumenthal'),
                          Bog(3, 'A Boy and His Dog at the End of the World', 1, 1, 5, 2019, 365, 'C. A. Fletcher'),
                          Film(4, 'Dune', 5, 0, 0, 1984, 'David Lynch', 137),
                          Film(5, '12 Angry Men', 2, 0, 0, 1957, 'Sidney Lumet', 96),
                          Film(6, 'Apocalypse Now', 5, 2, 0, 1979, 'Francis Ford Coppola', 147),
                          CD(7, 'The Number of the Beast', 3, 2, 0, 1982, 'Iron Maiden', 8, 39),
                          CD(8, 'A Night at the Opera', 2, 2, 4, 1975, 'Queen', 12, 43),
                          CD(9, 'Back in Black', 12, 12, 9, 1980, 'AC/DC', 10, 42),
                          DRMLicens(10, 'Alle mine morgener på jorden: Mit autodidakte liv', 5, 3, 0, 2017,
                                    'Troels Kløvedal',
                                    'Lydbog', 14),
                          DRMLicens(11, 'Gør det selv nr 10', 5, 2, 0, 'Bonniers', 2021, 'Online Magasin', 14),
                          DRMLicens(12, 'The Third man', 5, 5, 2, 1949, 'Orson Welles', 'Online Film', 1)
                          ]
        # itteration igennem dataset, kalder de enkelte objekters klassespecifikke .toSQL -metode og sender dem til
        # databasen via handlerens .runSQL metode. Data er nu gemt i databasen.
        for materiale in self.dataset:
            self.runSQL(materiale.toSQL('insert'))

    # metode sender SQL kode til databasen. Jeg har ikke beskyttet mod angreb med sqlInjection,
    # deraf mit parameternavn :)
    def runSQL(self, sqlInjection):
        # self.statusEcho(sqlInjection)
        self.cursor.execute(sqlInjection)
        self.conn.commit()

    # metode der returnerer et specifikt objekt fra en defineret tabel i db
    def makeObject(self, id, table):
        if table == 'BOG':
            for row in self.conn.execute(f'SELECT * FROM {table} WHERE ID={id}'):
                return Bog(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
        elif table == 'FILM':
            for row in self.conn.execute(f'SELECT * FROM {table} WHERE ID={id}'):
                return Film(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
        elif table == 'CD':
            for row in self.conn.execute(f'SELECT * FROM {table} WHERE ID={id}'):
                return CD(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        elif table == 'DRMLICENS':
            for row in self.conn.execute(f'SELECT * FROM {table} WHERE ID={id}'):
                return DRMLicens(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])

    # metode der returnerer alle objekter fra en defineret tabel i db. Returneres i en list
    def makeObjects(self, table):
        results = []
        # hvis tabellen der skal hentes data fra er 'BOG'
        if table == 'BOG':
            # send sql SELECT *, itterer igennem resultaterne og tilføj hvert resultat som obejekt til results
            for row in self.conn.execute(f'SELECT * FROM {table}'):
                results.append(Bog(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        elif table == 'FILM':
            for row in self.conn.execute(f'SELECT * FROM {table}'):
                results.append(Film(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        elif table == 'CD':
            for row in self.conn.execute(f'SELECT * FROM {table}'):
                results.append(CD(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        elif table == 'DRMLICENS':
            for row in self.conn.execute(f'SELECT * FROM {table}'):
                results.append(DRMLicens(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return results

    # returnerer materiale object hvis der findes et idmatch
    def findesMateriale(self, id):
        table_list = ['BOG', 'FILM', 'CD', 'DRMLICENS']
        for table_name in table_list:
            self.cursor.execute(f"SELECT ID FROM {table_name} WHERE ID={id}")
            if self.cursor.fetchone():
                return self.makeObject(id, table_name)
            else:
                continue
        return None

    # metode der nulstiller databasen, dvs dropper alle tables. Da denne klasse kun er en lille test, er det
    # lidt nemmere for mig at droppe alle tabeller i databasen inden jeg gemmer mine testdata hver gang jeg starter mit
    # program.
    def cleanDB(self):
        # dropper følgende tabeller
        self.cursor.execute('DROP TABLE IF EXISTS BOG')
        self.cursor.execute('DROP TABLE IF EXISTS FILM')
        self.cursor.execute('DROP TABLE IF EXISTS CD')
        self.cursor.execute('DROP TABLE IF EXISTS DRMLICENS')
        # udfører
        self.conn.commit()
        self.statusEcho('Databasen er ren')

    # metode der lukker forbindelsen til databasen
    def closeDB(self):
        self.conn.close()
        self.statusEcho('forbindelsen til databasen er lukket')

    # Metode der printer en besked - brugt til test
    def statusEcho(self, msgString):
        print(msgString)
