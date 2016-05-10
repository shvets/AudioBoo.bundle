from audioboo_service import AudiobooService

from audioboo_storage import AudiobooStorage

class PlexService(AudiobooService):
    def __init__(self):
        storage_name = Core.storage.abs_path(Core.storage.join_path(Core.bundle_path, 'Contents', 'audioboo.storage'))

        self.queue = AudiobooStorage(storage_name)
