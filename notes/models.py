from django.conf import settings
from django.db import models


class Note(models.Model):
	title = models.CharField(max_length=255)
	content = models.TextField()
	image = models.ImageField(upload_to='notes/', blank=True, null=True)
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name='notes',
	)

	def __str__(self):
		return self.title
from django.db import models

# Create your models here.
