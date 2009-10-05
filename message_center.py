
channel_list = []

message_queue = []

def add_channel(channel_name):
	global channel_list
	if channel_name not in channel_list:
		channel_list.append(channel_name)

add_channel("default")

def add_message(message, channel="default"):
	global message_queue, channel_list
	
	if channel not in channel_list:
		raise Exception("No channel: " + str(channel))
	
	message_queue.append((message, channel))

def get_message_with_channel():
	global message_queue
	if len(message_queue) > 0:
		return message_queue.pop(0)
	else:
		return (None, None)