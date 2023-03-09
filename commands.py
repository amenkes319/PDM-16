class Command:

    def __init__(self, conn):
        self.conn = conn
        self.curs = conn.cursor()
        self.commands = {
            "help": self._help,
            "signup": self._createAccount,
            "createCollection": self._createCollection,
            "listCollections": self._listCollection,
            "search": self._search,
            "done": self._done,
        }
        self.commandArgCount = {
            "help": 0,
            "signup": 5,
            "createCollection": 2,
            "listCollections": 0,
            "search": 0,
        }

    def execute(self, command, args):
        if command not in self.commands or len(args) != self.commandArgCount[command]:
            self.commands["help"]()
            return False

        if len(args) != self.argNums[command]:
            return False

        self.commands[command](*args)
        return True

    def _help(self):
        print("Commands:\n"
            "\t\"help\": prints this message\n"
            "\t\"signup <username> <password> <firstname> <lastname> <email>\": creates a new account\n"
            "\t\"createCollection <username> <name>\": creates a new collection\n"
            "\t\"listCollections\": lists all collections\n"
            "\t\"search\": searches for a collection")

    def _done(self):
        # shouldn't do anything
        pass

    def _createAccount(self, user, pw, firstname, lastname, email):
        self.curs.execute(
            "INSERT INTO account (username, password, firstname, lastname, email, creationDateTime, lastAccessDateTime) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (user, pw, firstname, lastname, email, "now()", "now()"))
        self.conn.commit()

    def _createCollection(self, username, name):
        self.curs.execute("SELECT MAX(CollectionID) FROM Collection WHERE Username = %s GROUP BY Username", (username,))
        
        collectionID = self.curs.fetchone()[0]
        if collectionID is None:
            collectionID = 1
        else:
            collectionID += 1

        self.curs.execute("INSERT INTO Collection (CollectionID, Username, Name) VALUES (%s, %s, %s)", (collectionID, username, name))
        self.conn.commit()

    def _listCollection(self):
        pass

    def _search(self):
        pass
