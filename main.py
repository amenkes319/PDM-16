from commands import Command
from configparser import ConfigParser
import psycopg2
from sshtunnel import SSHTunnelForwarder

def login():
    login = {"username": " ", "password": " "}
    parser = ConfigParser()
    parser.read('ssh_login.ini')
    params = parser.items('login')

    for param in params:
        login[param[0]] = param[1]
    username = login.get("username")
    password = login.get("password")
    return username, password

# multiple args in quotes (e.g. "hello world") wil get parsed to "Hello World" and gets rid of the quotes
# single words in quotes (e.g. "hello") will not get rid of the quotes
def combineQuotedArgs(args):
    newArgs = []
    i = 0
    while i < len(args):
        if args[i][0] == '"' and args[i][-1] != '"':
            j = i + 1
            while j < len(args) and args[j][-1] != '"':
                j += 1
            combinedArg = " ".join(args[i:j+1])
            newArgs.append(combinedArg[1:-1] if combinedArg.startswith('"') and combinedArg.endswith('"') else combinedArg)
            i = j + 1
        else:
            newArgs.append(args[i])
            i += 1
    return newArgs

def main():
    username, password = login()
    dbName = "p320_16"

    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=username,
                                ssh_password=password,
                                remote_bind_address=('localhost', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            params = {
                'database': dbName,
                'user': username,
                'password': password,
                'host': 'localhost',
                'port': server.local_bind_port
            }

            conn = psycopg2.connect(**params)
            print("Database connection established")

            running = True
            command = Command(conn)
            while running:
                userInput = input("> ")
                cmd = userInput.split(" ")[0]
                args = userInput.split(" ")[1:]
                args = combineQuotedArgs(args)

                valid = command.execute(cmd, args)
                if cmd == "quit":
                    running = False
    except Exception as e:
        print(e)
        print("Connection failed")
    finally:
        print("Connection closed")
        conn.close()

if __name__ == '__main__':
    main()