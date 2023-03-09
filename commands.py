class Command:

    def __init__(self, conn):
        self.conn = conn
        self.curs = conn.cursor()
        self.argNums = {
            "help": 0,
            "signup": 5,
            "createCollection": 0,
            "listCollections": 0,
            "search": 0,
            "done": 0,
        }
        self.commands = {
            "help": self._help,
            "signup": self._createAccount,
            "createCollection": self._createCollection,
            "listCollections": self._listCollection,
            "search": self._search,
            "done": self._done,
        }

    def execute(self, command, args):
        if command not in self.commands:
            return False

        if len(args) != self.argNums[command]:
            return False

        self.commands[command](*args)
        return True

    def _help(self):
        print("Help!")

    def _done(self):
        # shouldn't do anything
        pass

    def _createAccount(self, user, pw, firstname, lastname, email):
        self.curs.execute(
            "INSERT INTO account (username, password, firstname, lastname, email, creationDateTime, lastAccessDateTime) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (user, pw, firstname, lastname, email, "now()", "now()"))
        self.conn.commit()

    def _createCollection(self):
        pass

    def _listCollection(self):
        pass

    def _search(self):
        pass
