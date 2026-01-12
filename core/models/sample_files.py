import os
import shutil
from django.db import models
from django.utils.text import slugify
from django.conf import settings


def sample_file_upload_to(instance, filename):
    """
    Decide onde salvar o arquivo:
    - Sem collection → _unassigned_samples/sample_id/
    - Com collection → biobank/collection/sample_id/
    """
    sample = instance.sample

    if not sample.collection or not sample.biobank:
        return os.path.join(
            "_unassigned_samples",
            slugify(sample.sample_id),
            filename,
        )

    return os.path.join(
        slugify(sample.biobank.name),
        slugify(sample.collection.name),
        slugify(sample.sample_id),
        filename,
    )


class SampleFile(models.Model):
    sample = models.ForeignKey(
        "Sample",
        on_delete=models.CASCADE,
        related_name="files",
    )

    file = models.FileField(upload_to=sample_file_upload_to)
    description = models.TextField(blank=True, null=True)
    file_type = models.CharField(max_length=100, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


# =========================================================
# 🔥 MOVE FILES WHEN SAMPLE GETS A COLLECTION
# =========================================================
def move_sample_files(sample):
    """
    Move arquivos de _unassigned_samples para
    biobank/collection/sample_id
    """
    if not sample.collection or not sample.biobank:
        return

    old_base = os.path.join(
        settings.MEDIA_ROOT,
        "_unassigned_samples",
        slugify(sample.sample_id),
    )

    if not os.path.exists(old_base):
        return

    new_base = os.path.join(
        settings.MEDIA_ROOT,
        slugify(sample.biobank.name),
        slugify(sample.collection.name),
        slugify(sample.sample_id),
    )

    os.makedirs(new_base, exist_ok=True)

    for filename in os.listdir(old_base):
        shutil.move(
            os.path.join(old_base, filename),
            os.path.join(new_base, filename),
        )

    # remove pasta antiga se vazia
    if not os.listdir(old_base):
        os.rmdir(old_base)

