from py3xui import Api

# In this short example we will update the client's traffic limit.
# Due to the way API returns the data, we need to get the needed inbound to
# obtain the actual UUID of the client.
# Because other endpoints return the numeric ID of the client in the given inbound,
# not the UUID.
# In the same way it can be implemented for AsyncApi, the methods are called
# exactly the same way, and has the same signatures.

# 1️⃣ Create an instance of the API class.
host = "**************************"
username = "**********"
password = "**********"
api = Api(host, username, password)

# 2️⃣ Login to the API.
api.login()

user_email = "iwatkot"  # ⬅️ Your user email here.
inbound_id = 4  # ⬅️ Your inbound ID here.

# 3️⃣ Get the inbound.
inbound = api.inbound.get_by_id(inbound_id)
print(f"Inbound has {len(inbound.settings.clients)} clients")

# 4️⃣ Find the needed client in the inbound.
client = None
for c in inbound.settings.clients:
    if c.email == user_email:
        client = c
        break

if client:
    print(f"Found client with ID: {client.id}")  # ⬅️ The actual Client UUID.
else:
    raise ValueError(f"Client with email {user_email} not found")

cliend_uuid = client.id

# 5️⃣ Get the client by email.
client_by_email = api.client.get_by_email(user_email)
print(f"Client by email has ID: {client_by_email.id}")  # ⬅️ The numeric ID here.

# 6️⃣ Update the client with needed parameters.
client_by_email.total_gb = 1000 * 1024 * 1024  # ⬅️ Your value here.

# 7️⃣ Update the client ID so it will be UUID, not numeric.
client_by_email.id = cliend_uuid

# 8️⃣ Update the client.
api.client.update(client_by_email.id, client_by_email)

# We are done!  🎉
# In this example we set the maximum traffic for the user with email "iwatkot" to 1GB.


# In this example we'll create a connection string which can be used to add a new profile
# to the VPN application.

from py3xui import Inbound

XUI_EXTERNAL_IP = "**********"  # ⬅️ Your external IP here or domain name.
MAIN_REMARK = "gmfvbot"  # ⬅️ It can be any string.
SERVER_PORT = 443  # ⬅️ Your server port here.


def get_connection_string(inbound: Inbound, user_uuid: str, user_email: int) -> str:
    """Prepare a connection string for the given inbound, user UUID and telegram ID.

    Arguments:
        inbound (Inbound): The inbound object.
        user_uuid (str): The UUID of the user.
        user_email (int): The email of the user.

    Returns:
        str: The connection string.
    """
    public_key = inbound.stream_settings.reality_settings.get("settings").get("publicKey")
    website_name = inbound.stream_settings.reality_settings.get("serverNames")[0]
    short_id = inbound.stream_settings.reality_settings.get("shortIds")[0]

    connection_string = (
        f"vless://{user_uuid}@{XUI_EXTERNAL_IP}:{SERVER_PORT}"
        f"?type=tcp&security=reality&pbk={public_key}&fp=firefox&sni={website_name}"
        f"&sid={short_id}&spx=%2F#{MAIN_REMARK}-{user_email}"
    )

    return connection_string


# Now, if you want to create a QR code image from the connection string, you can use the
# qrcode library.
# Remember to install it first with `pip install qrcode`.

import os

import qrcode

# 1️⃣ Obtain the connection string.
user_email = "iwatkot"  # ⬅️ Your user email here.
connection_string = get_connection_string(inbound, "**********", user_email)

# 2️⃣ Create the QR code.
img = qrcode.make(connection_string)

# 3️⃣ Save the QR code to the file.
qrcode_path = os.path.join("qrcodes", f"{user_email}.png")
img.save(qrcode_path)

# Now you can use the `qrcode_path` to send the QR code to the user.

# This example demonstrates how to get server status and create a database backup

# 9️⃣ Get server status
server_status = api.server.get_status()
print(f"CPU Load: {server_status.cpu}%")
print(f"Memory Usage: {server_status.mem.current}/{server_status.mem.total} bytes")
print(f"Uptime: {server_status.uptime} seconds")

# 🔟 Create database backup
"""The get_db() method retrieves a database backup file and saves it locally.
The backup contains all XUI panel data including users, inbounds and settings.
"""
db_backup_path = "backup.db"
api.server.get_db(db_backup_path)
print(f"Database backup saved to {db_backup_path}")
