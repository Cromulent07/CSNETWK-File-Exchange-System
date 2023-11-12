# CSNETK-MP

## Description
CSNETWK MP is a File Exchange System, allowing clients to be able to store, share and fetch files from a single server TCP or UDP protocol 

## TODO

### Implement Input Commands
- [ ] Connect to the server application
- [ ] Disconnect to the server application
- [ ] Register a unique handle or alias
- [ ] Send file to server
- [ ] Request directory file list from a server
- [ ] Fetch a file from a server
- [ ] Request command help to output all Input
        Syntax commands for references

### Impelement System Messages
- [ ] Message upon successful connection to the server
- [ ] Message upon successful disconnection to the server
- [ ] Message upon successful registration of a handle or alias
- [ ] Message upon successful sending a file to server with timestamp
- [ ] Message upon successful receipt of the directory list from the server
- [ ] Message upon successful receipt of the requested file

### Implement Error Messages
- [ ] Message upon unsuccessful connection to the server due to the
server not running or incorrect IP and Port combination
- [ ] Message upon unsuccessful disconnection to the server due to not
currently being connected
- [ ] Message upon unsuccessful registration of a handle or alias due to
registered "handle" or alias already exists
- [ ] Message upon unsuccessful sending of a file that does not
exist in the client directory
- [ ] Message upon unsuccessful fetching of a file that does not
exist in the server directory
- [ ] Message due to command syntax
- [ ] Message due to incorrect or invalid parameters