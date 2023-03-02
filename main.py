from configparser import ConfigParser
import psycopg2
from sshtunnel import SSHTunnelForwarder

def main():
    login = {"username": " ", "password": " "}
    parser = ConfigParser()
    parser.read('ssh_login.ini')
    params = parser.items('login')
    dbName = "p320_16"

    for param in params:
        login[param[0]] = param[1]
    username = login.get("username")
    password = login.get("password")

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
            curs = conn.cursor()
            print("Database connection established")
            curs.execute("SELECT * FROM account")
            print(curs.fetchall())
    except:
        print("Connection failed")
    finally:
        conn.close()


if __name__ == '__main__':
    main()