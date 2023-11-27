# CSNETK-MP

## Description
CSNETWK MP is a File Exchange System, allowing clients to be able to store, share and fetch files from a single server TCP or UDP protocol 

## TODO

### Bugs
- [ ] C2
- [ ] C3
- [ ] C4
- [ ] D4
- [ ] F1
- [ ] F2
- [ ] F3

### Bonus
- [ ] GUI
- [x] Broadcast messaging feature
- [x] Unicast messaging feature

### Implement Input Commands
- [x] Connect to the server application
- [x] Disconnect to the server application
- [x] Register a unique handle or alias
- [x] Send file to server
- [x] Request directory file list from a server
- [x] Fetch a file from a server
- [x] Request command help to output all Input
        Syntax commands for references

### Impelement System Messages
- [x] Message upon successful connection to the server
- [x] Message upon successful disconnection to the server
- [x] Message upon successful registration of a handle or alias
- [x] Message upon successful sending a file to server with timestamp
- [x] Message upon successful receipt of the directory list from the server
- [x] Message upon successful receipt of the requested file

### Implement Error Messages
- [x] Message upon unsuccessful connection to the server due to the
server not running or incorrect IP and Port combination
- [x] Message upon unsuccessful disconnection to the server due to not
currently being connected
- [x] Message upon unsuccessful registration of a handle or alias due to
registered "handle" or alias already exists
- [x] Message upon unsuccessful sending of a file that does not
exist in the client directory
- [x] Message upon unsuccessful fetching of a file that does not
exist in the server directory
- [x] Message due to command syntax
- [x] Message due to incorrect or invalid parameters