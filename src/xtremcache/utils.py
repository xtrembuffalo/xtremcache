import hashlib

class Utils():
    """Useful functions for the whole application."""

    def get_app_name():
        return "xtremcache"

    def get_public_props(obj):
        return list(name for name in dir(obj) if not name.startswith('_'))

    def str_to_md5(val):
        return hashlib.md5(val.encode()).hexdigest()