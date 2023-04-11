import hashlib
import random
import string

class Command:
    def __init__(self, conn):
        self.conn = conn
        self.curs = conn.cursor()
        self.username = None
        self.commands = {
            "help": self._help,
            "signup": self._createAccount,
            "login": self._login,
            "logout": self._logout,
            "follow": self._follow,
            "lookup": self._lookup,
            "unfollow": self._unfollow,
            "play": self._play,
            "playCollection": self._playCollection,
            "createCollection": self._createCollection,
            "listCollections": self._listCollection,
            "addToCollection": self._addToCollection,
            "addAlbumToCollection": self._addAlbumToCollection,
            "removeAlbumFromCollection": self._removeAlbumFromCollection,
            "removeFromCollection": self._removeFromCollection,
            "deleteCollection": self._deleteCollection,
            "renameCollection": self._renameCollection,
            "search": self._search,
            "recommendMonth": self._recommendMonth,
            "recommendFriends": self._recommendFriends,
            "recommendGenres": self._recommendGenres,
            "recommendSongs": self._recommendSongs,
            "profile": self._profile,
            "quit": None,
        }
        self.commandArgCount = {
            "help": 0,
            "signup": 5,
            "login": 2,
            "logout": 0,
            "follow": 1,
            "lookup": 1,
            "unfollow": 1,
            "play": 1,
            "playCollection": 1,
            "createCollection": 1,
            "listCollections": 1,
            "addToCollection": 2,
            "addAlbumToCollection": 2,
            "removeAlbumFromCollection": 2,
            "removeFromCollection": 2,
            "deleteCollection": 1,
            "renameCollection": 2,
            "recommendMonth": 0,
            "recommendFriends": 0,
            "recommendGenres": 0,
            "recommendSongs": 0,
            "profile": 2,
            "search": 4,
        }

    def _help(self):
        print("""Commands:
            "help": prints this message
            "signup <username> <password> <firstname> <lastname> <email>": creates a new account
            "login <username> <password>": login in as username
            "logout": logout
            "follow <username>": follow another user
            "lookup <email>": look up a user by email
            "unfollow <username>": unfollow another user
            "play <title>": listen to a song
            "playCollection <name>": listen to an entire collection of songs
            "createCollection <name>": creates a new collection
            "deleteCollection <name>": deletes a collection
            "listCollections <username>": lists all collections
            "addToCollection <collection> <title>": add a song to a collection
            "addAlbumToCollection <album> <collection>": add an album to a collection
            "removeAlbumFromCollection <album> <collection>": remove an album from a collection
            "removeFromCollection <collection> <title>": remove a song from a collection
            "renameCollection <oldname> <newname>": rename a collection
            "search <searchBy> <searchTerm> <sortBy> <sortOrder>": searches for a song
            "recommendMonth: shows the top 50 most popular song of the month
            "recommendFriends: shows the top 50 most popular songs among your friends
            "recommendGenres: shows the top 5 most popular genres of the month
            "recommendSongs: recommends songs based on your play history and play history of similar users
            "quit": quits the program""")

    def execute(self, command, args):
        if command == "quit":
            return True

        if command not in self.commands or len(args) != self.commandArgCount[command]:
            self.commands["help"]()
            return False

        self.commands[command](*args)
        return True
    
    def _profile(self, username, searchType):
        self.curs.execute(
            """
            SELECT COUNT(collection.name) FROM account as account
            INNER JOIN collection collection on account.username = collection.username
            WHERE account.username = %s;
            """, (username,))
        collectionCount = self.curs.fetchone()

        if collectionCount == None:
            collectionCount = 0
        else:
            collectionCount = collectionCount[0]

        self.curs.execute(
            """
            SELECT COUNT(follower.followedusername) FROM account as account
            INNER JOIN following follower ON account.username = follower.followedusername
            WHERE username = %s;
            """, (username,))
        numFollowers = self.curs.fetchone()

        if numFollowers == None:
            numFollowers = 0
        else:
            numFollowers = numFollowers[0]

        self.curs.execute(
            """
            SELECT COUNT(follower.followedusername) FROM account as account
            INNER JOIN following follower ON account.username = follower.followerusername
            WHERE username = %s;
            """, (username,))
        numFollowing = self.curs.fetchone()

        if numFollowing == None:
            numFollowing = 0
        else:
            numFollowing = numFollowing[0]
        print("User Profile for:", username)
        print(" Number of collections:", str(collectionCount))
        print(" Number of followers:", str(collectionCount))
        print(" Number of following:", str(collectionCount))
        if (searchType == "collection"):
            self.curs.execute(
                """
                SELECT a.name, COUNT(cc.songid)
                FROM account as ac
                INNER JOIN collectioncontains AS cc ON (cc.username = ac.username)
                INNER JOIN song AS s ON (s.songid = cc.songid)
                INNER JOIN songbyartist AS sba ON (s.songid = sba.songid)
                INNER JOIN artist AS a ON (a.artistid = sba.artistid)
                WHERE ac.username LIKE %s
                GROUP BY a.name, ac.username
                ORDER BY COUNT(cc.songid) DESC
                LIMIT 10
                """, (username,))
        else:
            self.curs.execute(
                """
                SELECT artist.name as artist, COUNT(l.songid) as plays FROM account as a
                INNER JOIN listen as l on a.username = l.username
                INNER JOIN songbyartist as sba on sba.songid = l.songid
                INNER JOIN artist as artist on sba.artistid = artist.artistid
                WHERE a.username = %s
                GROUP BY artist.name
                ORDER BY COUNT(l.songid) DESC LIMIT 10;
            """, (username,))
        
        print(" Top 10 artists: ")
        r = 1
        for row in self.curs.fetchall():
            name = row[0]
            numPlays = row[1]
            print(" "+str(r)+".", name)
            r += 1

    def _removeAlbumFromCollection(self, album, collection):
        if self.username == None:
            print("Login to modifiy a collection.")
            return True
        
        self.curs.execute(
            """
            SELECT * FROM collection
            WHERE name LIKE %s AND
            username LIKE %s
            """, (collection, self.username))
        
        collectionData = self.curs.fetchone()
        if collectionData == None:
            print("No collection by that name")
            return False

        self.curs.execute(
            """
            SELECT albumid FROM album
            WHERE name LIKE %s
            """, (album,))

        album_id = self.curs.fetchone()
        if album_id == None:
            print("No album by that name")
            return False
        
        self.curs.execute(
            """
            SELECT songid FROM onalbum
            WHERE albumid = %s
            """, (album_id))
        
        song_ids = self.curs.fetchall()
        if song_ids == None:
            print("No songs in that album")
            return False

        self.curs.execute(
                """
                SELECT songid FROM collectioncontains
                WHERE collectionid = %s AND
                username = %s
                """, (collectionData[0], self.username))
        songs_in_collection = self.curs.fetchall()
        for song_id in song_ids:
            if (song_id in songs_in_collection):
                self.curs.execute(
                    """
                    DELETE FROM collectioncontains
                    WHERE collectionid = %s AND
                    username = %s AND
                    songid = %s
                    """, (collectionData[0], self.username, song_id[0]))
                print("removed song with id: ", song_id[0])

                self.conn.commit()

        return True

    
    def _addAlbumToCollection(self, album, collection):
        if self.username == None:
            print("Login to modifiy a collection.")
            return True
        
        self.curs.execute(
            """
            SELECT * FROM collection
            WHERE name LIKE %s AND
            username LIKE %s
            """, (collection, self.username))
        
        collectionData = self.curs.fetchone()
        if collectionData == None:
            print("No collection by that name")
            return False

        self.curs.execute(
            """
            SELECT albumid FROM album
            WHERE name LIKE %s
            """, (album,))

        album_id = self.curs.fetchone()
        if album_id == None:
            print("No album by that name")
            return False
        
        self.curs.execute(
            """
            SELECT songid FROM onalbum
            WHERE albumid = %s
            """, (album_id))
        
        song_ids = self.curs.fetchall()
        if song_ids == None:
            print("No songs in that album")
            return False

        self.curs.execute(
                """
                SELECT songid FROM collectioncontains
                WHERE collectionid = %s AND
                username = %s
                """, (collectionData[0], self.username))
        songs_in_collection = self.curs.fetchall()
        for song_id in song_ids:
            if not (song_id in songs_in_collection):
                self.curs.execute(
                    """
                    INSERT INTO collectioncontains(collectionid, username, songid)
                    VALUES(%s, %s, %s)
                    """, (collectionData[0], self.username, song_id[0]))
                print("adding song with id: ", song_id[0])

                self.conn.commit()
            else:
                print("song already in collection")

        return True

    def _lookup(self, email):
        self.curs.execute(
            """
            SELECT username FROM account 
            WHERE email LIKE %s
            """, (f"%{email}%",))

        print("Username")
        for row in self.curs.fetchall():
            print(row[0])
        return True

    def _logout(self):
        if self.username == None:
            print("Not currently logged in.")
            return False
        
        print("Logged out of: " + self.username)
        self.username = None
        return True

    def _renameCollection(self, collectionName, newName):
        if self.username == None:
            print("Login to rename a collection.")
            return True
        
        self.curs.execute(
            """
            SELECT * FROM collection
            WHERE name LIKE %s AND
            username LIKE %s
            """, (collectionName, self.username))
        
        collectionData = self.curs.fetchone()
        if collectionData == None:
            print("Couldn't find collection")
            return False
    
        collectionid = collectionData[0]
        self.curs.execute(
            """
            UPDATE collection
            SET name = %s
            WHERE collectionid = %s AND
            username LIKE %s
            """, (newName, collectionid, self.username))
        self.conn.commit()
        print("Renamed collection")
        return True

    def _deleteCollection(self, collection):
        if self.username == None:
            print("Login to delete a collection.")
            return True

        self.curs.execute(
            """
            DELETE FROM collectioncontains
            WHERE collectionid IN
                (SELECT collectionid
                FROM collection
                WHERE name = %s AND username = %s)
            AND username = %s   
            """, (collection, self.username, self.username))
        self.conn.commit()

        self.curs.execute(
            """
            DELETE FROM collection
            WHERE name = %s AND
            username = %s
            """, (collection, self.username))
        self.conn.commit()
        print("Deleted collection")

        return True

    def _removeFromCollection(self, collection, song):
        if self.username == None:
            print("Login to remove a song from a collection.")
            return True
        
        self.curs.execute(
            """
            SELECT * FROM song
            WHERE title LIKE %s
            """, (song,))
        
        songData = self.curs.fetchone()
        if songData == None:
            print("Couldn't find song")
            return False

        self.curs.execute(
            """
            SELECT * FROM collection
            WHERE name LIKE %s AND
            username LIKE %s
            """, (collection, self.username))
        
        collectionData = self.curs.fetchone()
        if collectionData == None:
            print("Couldn't find collection")
            return False
        
        songid = songData[0]
        collectionid = collectionData[0]
        self.curs.execute(
            """
            DELETE FROM collectioncontains
            WHERE collectionid = %s AND
            username = %s AND
            songid = %s
            """, (collectionid, self.username, songid))
        self.conn.commit()
        print("Removed song from collection")

        return True
    
    def _addToCollection(self, collection, song):
        if self.username == None:
            print("Login to add to a collection.")
            return True
        
        self.curs.execute(
            """
            SELECT * FROM song
            WHERE title LIKE %s
            """, (song,))
        
        songData = self.curs.fetchone()
        if songData == None:
            print("Couldn't find song")
            return False

        self.curs.execute(
            """
            SELECT * FROM collection
            WHERE name LIKE %s AND
            username LIKE %s
            """, (collection, self.username))
        
        collectionData = self.curs.fetchone()
        if collectionData == None:
            print("Couldn't find collection")
            return False
        
        songid = songData[0]
        collectionid = collectionData[0]
        self.curs.execute(
            """
            INSERT INTO collectioncontains(collectionid, username, songid)
            VALUES (%s, %s, %s)
            """, (collectionid, self.username, songid))
        self.conn.commit()
        print("Added song to collection")

        return True

    def _play(self, song):
        if self.username == None:
            print("Login to play music")
            return True
        
        self.curs.execute(
            """
            SELECT * FROM song
            WHERE title LIKE %s
            """, (song,))
        
        songData = self.curs.fetchone()

        if songData == None:
            print("Couldn't find any songs by that title")
            return True
        songid = songData[0]
            
        self.curs.execute(
            """
            INSERT INTO listen(username, songid, listendatetime)
            VALUES (%s, %s, %s)
            """, (self.username, songid, "now()"))
        self.conn.commit()
        print("Listened to:", song)
        return True

    def _playCollection(self, collection):
        if self.username == None:
            print("Login to play music")
            return True
        
        self.curs.execute(
            """
            SELECT * FROM collection
            WHERE name LIKE %s AND
            username LIKE %s
            """, (collection, self.username))
        
        collectionData = self.curs.fetchone()

        if collectionData == None:
            print("Couldn't find collections by that name")
            return True
        collectionId = collectionData[0]

        self.curs.execute(
            """
            SELECT songid FROM collectioncontains
            WHERE collectionid = %s
            AND username = %s
            """, (collectionId, self.username))
        
        collectionSongIds = self.curs.fetchall()
        if collectionSongIds == None:
            print("No songs in collection")
            return False
        
        for songid in collectionSongIds:
            self.curs.execute(
                """
                INSERT INTO listen(username, songid, listendatetime)
                VALUES (%s, %s, %s)
                """, (self.username, songid, "now()"))
            self.conn.commit()
        print("Listened to entire collection")

        return True

    def _follow(self, otheruser):
        if self.username == None:
            print("Login to follow another user")
            return True

        self.curs.execute(
            """
            SELECT * FROM following
            WHERE followerusername = %s AND
            followedusername = %s
            """, (self.username, otheruser))
        
        followingData = self.curs.fetchone()
        if (followingData != None):
            print("You are already following that user")
            return False

        self.curs.execute(
            """
            INSERT INTO following(followerusername, followedusername)
            VALUES (%s, %s)
            """, (self.username, otheruser))
        self.conn.commit()
        print("You are now following: ", otheruser)
        return True
    
    def _unfollow(self, otheruser):
        if self.username == None:
            print("Login to unfollow another user")
            return True

        self.curs.execute(
            """
            SELECT * FROM following
            WHERE followerusername = %s AND
            followedusername = %s
            """, (self.username, otheruser))
        
        followingData = self.curs.fetchone()
        if (followingData == None):
            print("You not following that user")
            return False

        self.curs.execute(
            """
            DELETE FROM following
            WHERE followerusername = %s AND
            followedusername = %s
            """, (self.username, otheruser))
        self.conn.commit()
        print("Unfollowed: ", otheruser)
        return True

    def _login(self, username, password):
        self.curs.execute(
            """
            SELECT salt FROM account as a
            WHERE a.username = %s
            """ , (username,))
        salt = self.curs.fetchone()

        if (salt == None):
            print("Incorrect login information")
            return False
        salt = salt[0]
        password = password + salt

        password = hashlib.sha256(password.encode('UTF-8')).hexdigest()
        self.curs.execute(
            """
            SELECT * FROM account as a 
            WHERE a.username = %s AND
            a.password = %s
            """, (username, password))
        
        accountData = self.curs.fetchone()
        if (accountData == None):
            print("Incorrect login information")
            return False
        
        self.curs.execute(
            """
            UPDATE account
            SET lastaccessdatetime = %s
            WHERE username = %s
            """, ("now()", username))
        self.conn.commit()

        print("Logged in as: " + accountData[0])
        self.username = accountData[0]
        return True

    def _help(self):
        print("""Commands:
            "help": prints this message
            "signup <username> <password> <firstname> <lastname> <email>": creates a new account
            "login <username> <password>": login in as username
            "logout": logout
            "follow <username>": follow another user
            "lookup <email>": look up a user by email
            "unfollow <username>": unfollow another user
            "play <title>": listen to a song
            "playCollection <name>": listen to an entire collection of songs
            "createCollection <name>": creates a new collection
            "deleteCollection <name>": deletes a collection
            "listCollections <username>": lists all collections
            "addToCollection <collection> <title>": add a song to a collection
            "addAlbumToCollection <album> <collection>": add an album to a collection
            "removeAlbumFromCollection <album> <collection>": remove an album from a collection
            "removeFromCollection <collection> <title>": remove a song from a collection
            "renameCollection <oldname> <newname>": rename a collection
            "search <searchBy> <searchTerm> <sortBy> <sortOrder>": searches for a song
            "profile <username> <searchTerm>": displays a user's profile (searchTerm='collection' or 'plays')
            "quit": quits the program""")

    def _createAccount(self, user, pw, firstname, lastname, email):
        salt = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

        pw += salt
        pw = hashlib.sha256(pw.encode('UTF-8')).hexdigest()
        self.curs.execute(
            """
            INSERT INTO account (username, password, salt, firstname, lastname, email, creationDateTime, lastAccessDateTime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user, pw, salt, firstname, lastname, email, "now()", "now()"))
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
            JOIN CollectionContains cc ON c.CollectionID = cc.CollectionID AND c.username = cc.username 
            JOIN Song s ON cc.SongId = s.SongID 
            WHERE c.Username = %s 
            GROUP BY c.Name 
            ORDER BY c.Name ASC
            """, (username,))
        print("Collection Name | Number of Songs | Length (min)")
        print("--------------------------------------------------------------")
        for row in self.curs.fetchall():
            name = row[0]
            numSongs = row[1]
            length = row[2] / 60
            print(name, "|", numSongs, "|", "{:.2f}".format(length))

    def _recommendMonth(self):
        self.curs.execute(
            """
            SELECT s.title, count(s.songid) as num
            FROM song AS s INNER JOIN listen AS l
            ON (s.songid = l.songid)
            WHERE l.listendatetime > (now() - INTERVAL '30 00:00:00.0' DAY TO SECOND)
            GROUP BY s.songid
            ORDER BY num DESC
            LIMIT 50;
            """)
        print("Song Name | Listens in the last 30 Days")
        print("---------------------------------------")
        for row in self.curs.fetchall():
            name = row[0]
            numPlays = row[1]
            print(name, "|", numPlays, "|")

    def _recommendFriends(self):
        if self.username == None:
            print("Login to follow another user")
            return True

        self.curs.execute(
            """
            SELECT s.title, count(s.songid) as num
            FROM song AS s INNER JOIN listen AS l
            ON (s.songid = l.songid)
            INNER JOIN following AS f
            ON (l.username = f.followedusername)
            WHERE f.followerusername = %s
            GROUP BY s.songid
            ORDER BY num DESC
            LIMIT 50;
            """, self.username)
        print("Song Name | Listens")
        print("-------------------")
        for row in self.curs.fetchall():
            name = row[0]
            numPlays = row[1]
            print(name, "|", numPlays, "|")

    def _recommendGenres(self):
        pass

    def _recommendSongs(self):
        pass

    def _search(self, searchBy, searchTerm, sortBy, sortOrder):
        searchTerm = searchTerm.lower()
        sortOrder = sortOrder.upper()
        searchBy = searchBy.lower()
        sortBy = sortBy.lower()

        if searchBy not in {"title", "artist", "genre", "album"}:
            print("searchBy must be title, artist, genre, or album")
            return

        if sortBy not in {"title", "artist", "genre", "year"}:
            print("sortBy must be title, artist, genre, or year")
            return

        if (sortOrder != "ASC" and sortOrder != "DESC"):
            sortOrder = "ASC" # default value: asc

        searchTitle = searchArtist = searchAlbum = searchGenre = "☺"

        if searchBy == "title":
            searchTitle = searchTerm
        elif searchBy == "artist":
            searchArtist = searchTerm
        elif searchBy == "genre":
            searchGenre = searchTerm
        elif searchBy == "album":
            searchAlbum = searchTerm

        if sortBy == "title":
            sortBy = "s.Title"
        elif sortBy == "artist":
            sortBy = "ar.name"
        elif sortBy == "genre":
            sortBy = "g.name"
        elif sortBy == "year":
            sortBy = "EXTRACT (YEAR FROM s.releasedate)"

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
            GROUP BY s.Title, ar.Name, al.Name, s.Length, s.releasedate, g.name
            ORDER BY """ + sortBy + """ """ + sortOrder + """
            """, (f"%{searchTitle}%", f"%{searchArtist}%", f"%{searchAlbum}%", f"%{searchGenre}%"))

        for row in self.curs.fetchall():
            title = row[0]
            artist = row[1]
            album = row[2]
            length = row[3] / 60
            listenCount = row[4]

            print(title, "|", artist, "|", album, "|", length, "|", listenCount)
