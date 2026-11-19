from hashlib import sha256
from pathlib import Path


def snapshot_fingerprint():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    fingerprint = sha256()

    for filename in ("events_snapshot.json", "venues_snapshot.json"):
        file_digest = sha256((data_dir / filename).read_bytes()).digest()
        fingerprint.update(file_digest)

    return fingerprint.hexdigest()