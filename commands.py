class Command:

    def __init__(self, conn):
        self.conn = conn
        self.curs = conn.cursor()
        self.commands = {
            "signup": self._createAccount,
            "createCollection": self._createCollection,
            "listCollections": self._listCollection,
            "search": self._search,
        }

    
    def execute(self, command, *args):
        if command not in self.commands:
            return False
        
        self.commands[command](*args)
        return True

    def _createAccount(self, user, pw, firstname, lastname, email):
        self.curs.execute("INSERT INTO account (username, password, firstname, lastname, email, creationDateTime, lastAccessDateTime) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user, pw, firstname, lastname, email, "now()", "now()"))
        self.conn.commit()

    def _createCollection(self):
        pass

    def _listCollection(self):
        pass

    def _search(self):
        pass