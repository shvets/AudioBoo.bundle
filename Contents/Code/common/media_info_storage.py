from storage import Storage
from file_storage import FileStorage

class MediaInfoStorage(FileStorage):
    def __init__(self, file_name):
        FileStorage.__init__(self, file_name)

        self.simple_types = []

    def register_simple_type(self, name):
        if name not in self.simple_types:
            return self.simple_types.append(name)

    def find(self, search_item):
        MediaInfoStorage.sanitize(search_item)

        found = None

        for item in self.data:
            type = search_item['type']

            if item['path'] == search_item['path']:
                if type in  self.simple_types:
                    found = item

                elif type == 'season':
                    if 'season' in item:
                        if item['season'] == search_item['season']:
                            if not 'episode' in item:
                                found = item
                    break

                elif type == 'episode':
                    if 'season' in item and 'season' in search_item:
                        if item['season'] == search_item['season']:
                            if 'episode' in item and 'episode' in search_item:
                                if item['episode'] == search_item['episode']:
                                    found = item
                    break

        return found

    def add(self, item):
        bookmark = self.find(item)

        if not bookmark:
            Storage.add(self, item)

            self.save()

    def remove(self, item):
        bookmark = self.find(item)

        if bookmark:
            Storage.remove(self, item)

            self.save()

    def load_storage(self):
        return FileStorage.load_storage(self)

    def save_storage(self, data):
        FileStorage.save_storage(self, data)
