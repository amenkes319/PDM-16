class Command:
    def __init__(self, conn):
        self.conn = conn
        self.curs = conn.cursor()

    def createAccount(self, user, pw, firstname, lastname, email):
        self.curs.execute("INSERT INTO account (username, password, firstname, lastname, email, creationDateTime, lastAccessDateTime) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user, pw, firstname, lastname, email, "now()", "now()"))
        self.conn.commit()
