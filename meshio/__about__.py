try:
    # Python 3.8
    from importlib import metadata
except ImportError:
    try:
        import importlib_metadata as metadata
    except ImportError:
        print("Meshio version cannot be determined for this install.")

try:
    __version__ = metadata.version("meshio")
except Exception:
    __version__ = "unknown"
