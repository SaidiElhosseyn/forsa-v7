import re
import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage


class CloudinaryStorage(Storage):
    def _save(self, name, content):
        result = cloudinary.uploader.upload(
            content,
            folder="forsa",
            use_filename=True,
            unique_filename=True,
            overwrite=False,
            resource_type="auto",
        )
        # Store the full HTTPS URL so url() never needs to reconstruct it
        return result["secure_url"]

    def url(self, name):
        if not name:
            return ""
        # Already a full Cloudinary URL (normal case)
        if name.startswith("http"):
            return name
        # Fallback: reconstruct from public_id
        return cloudinary.CloudinaryImage(name).build_url()

    def exists(self, name):
        return False

    def delete(self, name):
        try:
            if name.startswith("http"):
                m = re.search(r"/upload/(?:v\d+/)?(.+?)(?:\.\w+)?$", name)
                public_id = m.group(1) if m else name
            else:
                import os
                public_id = os.path.splitext(name)[0]
            cloudinary.uploader.destroy(public_id)
        except Exception:
            pass

    def _open(self, name, mode="rb"):
        raise NotImplementedError("CloudinaryStorage does not support open()")

    def size(self, name):
        return 0

    def get_available_name(self, name, max_length=None):
        return name
