from audioboo_service import AudiobooService

from plex_storage import PlexStorage

class AudiobooPlexService(AudiobooService):
    def __init__(self):
        storage_name = Core.storage.abs_path(Core.storage.join_path(Core.bundle_path, 'Contents', 'audioboo.storage'))

        self.queue = PlexStorage(storage_name)

        self.queue.register_simple_type('author')
        self.queue.register_simple_type('tracks')
