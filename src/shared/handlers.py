from threading import Lock


class CHandler:
    def __init__(self):
        self.cancelled_handlers = {}
        self.data_storage = {}
        self.active_callbacks = {}
        self.photo_lock = Lock()

    def store_data(self, chat_id, data_name, data):
        try:
            if not chat_id in self.data_storage:
                self.data_storage[chat_id] = {}
            self.data_storage[chat_id][data_name] = data
        except Exception: pass

    def pop_data(self, chat_id, data_name):
        try:
            if not chat_id in self.data_storage.keys():
                return None
            if not data_name in self.data_storage[chat_id].keys():
                return None
            data = self.data_storage[chat_id][data_name]
            del self.data_storage[chat_id][data_name]
            return data
        except Exception:
            return None

    def safe_pop_data(self, chat_id, data_name):
        try:
            if not chat_id in self.data_storage.keys():
                return None
            if not data_name in self.data_storage[chat_id].keys():
                return None
            return self.data_storage[chat_id][data_name]
        except Exception: pass

    def add_callback(self, chat_id, callback):
        try:
            self.active_callbacks[chat_id] = callback
        except Exception: pass

    def has_callback(self, chat_id):
        try:
            if not type(chat_id) == int: return
            return chat_id in self.active_callbacks.keys()
        except Exception: pass

    def get_callback(self, chat_id):
        try:
            with self.photo_lock:
                if not chat_id in self.active_callbacks.keys():
                    return lambda _: None

                c = self.active_callbacks[chat_id]
                del self.active_callbacks[chat_id]
                return c
        except Exception: pass

    def remove_callback(self, chat_id):
        try:
            self.active_callbacks[chat_id] = None
            del self.active_callbacks[chat_id]
        except Exception: pass

