# 247csa

 247csa

+-------------------+         WebSocket         +-----------------------------+
|   User Browser    |  --------------------->  | Django Channels (Consumer)  |
| (chat_widget.html)|   JSON: {message, ...}   |   (platform_connections/    |
|                   |                          |     consumers.py)           |
+-------------------+                          +-----------------------------+
         |                                               |
         |                                               |
         |                                               v
         |                                   1. Checks session active
         |                                   2. Saves message to DB
         |                                   3. Broadcasts to group
         |                                               |
         |                                               v
+-------------------+         WebSocket         +-----------------------------+
|   Agent Browser   |  <---------------------  |   All Connected Clients      |
| (chat_window.html)|   JSON: {message, ...}   |   (user, agent, etc.)       |
+-------------------+                          +-----------------------------+