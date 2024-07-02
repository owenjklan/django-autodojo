"""
The unit tests for the autodojo lib require some ORM
models to be defined. Note: We don't actually need a database
behind these, as we're only testing what AutoDojo will
create when fed these model definitions.
"""

from django.db import models


class ChildModel(models.Model):
    """
    This class represents the simplest of ORM/DB models:
    all simple fields, no foreign keys etc.
    """

    count = models.IntegerField()
    name = models.TextField()

    class Meta:
        # We need to specify this to ensure the model resolution will work
        app_label = "autodojo"


class ForeignKeyParentModel(models.Model):
    """
    This class is intended to provide a very simple foreign
    key relationship.
    """

    dummy = models.ForeignKey(ChildModel, on_delete=models.CASCADE)
    relation = models.TextField()

    class Meta:
        # We need to specify this to ensure the model resolution will work
        app_label = "autodojo"


class ManyToManyParentModel(models.Model):
    """
    This class is intended to represent M2M relationships between
    two models where forward and reverse relations are defined.
    """

    name = models.TextField()
    children = models.ManyToManyField("ChildModel", related_name="parents")

    class Meta:
        # We need to specify this to ensure the model resolution will work
        app_label = "autodojo"
