class Command:

    def __init__(self, conn):
        self.conn = conn
        self.curs = conn.cursor()
        self.username = None
        self.commands = {
            "help": self._help,
            "signup": self._createAccount,
            "login": self._login,
            "createCollection": self._createCollection,
            "listCollections": self._listCollection,
            "search": self._search,
            "quit": None,
        }
        self.commandArgCount = {
            "help": 0,
            "signup": 5,
            "login": 2,
            "createCollection": 1,
            "listCollections": 1,
            "search": 1,
        }

    def execute(self, command, args):
        if command == "quit":
            return True

        if command not in self.commands or len(args) != self.commandArgCount[command]:
            self.commands["help"]()
            return False

        self.commands[command](*args)
        return True

    def _login(self, username, password):
        self.curs.execute(
            """
            SELECT * FROM account as a 
            WHERE a.username = %s AND
            a.password = %s
            """, (username, password))
        
        success = self.curs.fetchone()
        if (success == None):
            return False
        
        print("Logged in as: " + success[0])
        self.username = success[0]
        return True

    def _help(self):
        print("""Commands:
            "help": prints this message
            "signup <username> <password> <firstname> <lastname> <email>": creates a new account
            "login <username> <password.": login in as username
            "createCollection <name>": creates a new collection
            "listCollections <username>": lists all collections
            "search <searchterm>": searches for a collection
            "quit": quits the program""")

    def _createAccount(self, user, pw, firstname, lastname, email):
        self.curs.execute(
            """
            INSERT INTO account (username, password, firstname, lastname, email, creationDateTime, lastAccessDateTime)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user, pw, firstname, lastname, email, "now()", "now()"))
        self.conn.commit()

    def _createCollection(self, name):
        if self.username == None:
            print("Login to create a collection.")
            return True
        self.curs.execute(
            """
            SELECT COALESCE(MAX(CollectionID), 0) AS max_collection_id
            FROM Collection
            WHERE Username = %s
            """, (self.username,))
        
        collectionID = self.curs.fetchone()[0]
        if collectionID is None:
            collectionID = 1
        else:
            collectionID += 1

        self.curs.execute(
            """
            INSERT INTO Collection (CollectionID, Username, Name)
            VALUES (%s, %s, %s)
            """, (collectionID, self.username, name))
        self.conn.commit()

    def _listCollection(self, username):
        self.curs.execute(
            """
            SELECT c.Name AS CollectionName, 
                COUNT(cc.SongId) AS NumberOfSongs, 
                SUM(s.Length) AS TotalDuration 
            FROM Collection c 
            JOIN CollectionContains cc ON c.CollectionID = cc.CollectionID 
            JOIN Song s ON cc.SongId = s.SongID 
            WHERE c.Username = %s 
            GROUP BY c.Name 
            ORDER BY c.Name ASC
            """, (username,))
        for row in self.curs.fetchall():
            print(row)        

    def _search(self, searchTerm):
        searchTerm = searchTerm.lower()
        self.curs.execute(
            """
            SELECT s.Title AS SongName, ar.Name AS ArtistName, al.Name AS AlbumName, 
                s.Length AS SongLength, COUNT(l.SongID) AS ListenCount
            FROM Song s 
            JOIN SongByArtist sa ON s.SongID = sa.SongID
            JOIN Artist ar ON sa.ArtistID = ar.ArtistID
            JOIN OnAlbum oa ON s.SongID = oa.SongID
            JOIN Album al ON oa.AlbumID = al.AlbumID
            JOIN SongGenre sg ON s.SongID = sg.SongID
            JOIN Genre g ON sg.GenreID = g.GenreID
            JOIN Listen l ON s.SongID = l.SongID
            WHERE LOWER(s.Title) LIKE %s OR LOWER(ar.Name) LIKE %s OR LOWER(al.Name) LIKE %s OR LOWER(g.Name) LIKE %s
            GROUP BY s.Title, ar.Name, al.Name, s.Length 
            ORDER BY s.Title ASC, ar.Name ASC;
            """, (f"%{searchTerm}%", f"%{searchTerm}%", f"%{searchTerm}%", f"%{searchTerm}%"))

        for row in self.curs.fetchall():
            print(row)
