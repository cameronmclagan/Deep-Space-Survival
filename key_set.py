import event

class KeySet(event.EventDispatcher):
	def __init__(self):
		self.dict = {}

	def add_key(self, key_name):
		if key_name not in self.dict:
			self.dict[key_name] = True
			self.dispatch_event('on_add', key_name)
			self.dispatch_event('on_change', self)
	
	def rem_key(self, key_name):
		if key_name in self.dict:
			del self.dict[key_name]
			self.dispatch_event('on_rem', key_name)
			self.dispatch_event('on_change', self)
	
	def set_key_val(self, key_name, val):
		if key_name not in self.dict:
			self.add_key(key_name)
		
		self.dict[key_name] = val
		self.dispatch_event('on_set', key_name, val)
		self.dispatch_event('on_change', self)
	
	def has_key(self, key_name):
		if key_name in self.dict:
			return True
		else:
			return False
	
	def copy(self):
		copy_set = KeySet()
		copy_set.dict = self.dict.copy()

KeySet.register_event_type('on_add')
KeySet.register_event_type('on_rem')
KeySet.register_event_type('on_set')
KeySet.register_event_type('on_change')
