/*
 Users will be able to create new accounts and access via login.
 The system must record the date and time an account is created.
 It must also stored the date and time an user access into the application
 */
INSERT INTO User(Username, Password, FirstName, LastName, Email, CreationDate-Time, LastAccessDateTime)
    VALUES("username", "password", "firstname", "lastname", "email@gmail.com", time, last_access)

/*
 Users will be able to create collections of music.
 */
INSERT INTO Collection(CollectionID, Username, Name)
    VALUES(id, username, collection_name)

/*
  Users will be able to see the list of all their collections by name in ascending order.
    The list must show the following information per collection:
    – Collection’s name
    – Number of songs in the collection
    – Total duration in minutes
 */
 SELECT Name as collection_name from Collection, S

-- getting the number of songs in a collection:
 SELECT name from CollectionContains cc, Collection c WHERE cc.CollectionId ==