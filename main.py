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

            command = Command(conn)
            command.execute("signup", "test", "test", "test", "test", "test")
    except:
        print("Connection failed")
    finally:
        conn.close()

if __name__ == '__main__':
    main()