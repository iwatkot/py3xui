from py3xui import Api

# In this short example we will update the client's traffic limit.
# Due to the way API returns the data, we need to get the needed inbound to
# obtain the actual UUID of the client.
# Becaue other endpoints return the numeric ID of the client in the given inbound,
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
