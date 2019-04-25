from tortoise.models import Model
from tortoise import fields


class BookSummary(Model):
    isbn = fields.CharField(max_length=80, unique=True)
    title = fields.TextField()
    volume = fields.CharField(max_length=80)
    series = fields.CharField(max_length=80)
    author = fields.TextField()
    publisher = fields.CharField(max_length=80)
    pubdate = fields.CharField(max_length=80)
    cover = fields.TextField()
    published_at = fields.DateField(null=True)

    def __str__(self):
        return self.title
