from app.probe import send_message

# Send a message to the Paltalk room
result = send_message("A Welcome Soap Box", "Good Morning Soap Box", activate=True)
print("Send message result:", result)
