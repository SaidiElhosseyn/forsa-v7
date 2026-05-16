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
        )
        return result["public_id"]

    def url(self, name):
        if not name:
            return ""
        return cloudinary.CloudinaryImage(name).build_url()

    def exists(self, name):
        return False

    def delete(self, name):
        try:
            cloudinary.uploader.destroy(name)
        except Exception:
            pass

    def _open(self, name, mode="rb"):
        raise NotImplementedError("CloudinaryStorage does not support open()")

    def size(self, name):
        return 0

    def get_available_name(self, name, max_length=None):
        return name
