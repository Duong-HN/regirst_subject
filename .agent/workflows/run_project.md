---
description: How to run the Distributed Course Registration System
---

This workflow guides you through setting up the database, starting the server, and running the client.

1. **Setup Database**
   Initialize the MySQL database with the required schema and data.
   ```powershell
   cd setup_database
   python database_setup.py
   ```

2. **Start Server**
   Run the TCP server to listen for client connections.
   ```powershell
   cd server
   python server.py
   ```
   *Alternatively, run `server/run_server.bat`*

3. **Start Client**
   Run the client application to interact with the system. You can open multiple terminals to simulate multiple users.
   ```powershell
   cd client
   python client.py
   ```
   *Alternatively, run `client/run_client.bat`*
