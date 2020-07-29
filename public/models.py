from django.db import models
from django.contrib.postgres.fields import ArrayField


class Entity(models.Model):
    id = models.BigAutoField(primary_key=True)


class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()


class ItemWithIndex(models.Model):
    """Only testing filtering speed with this model"""
    id = models.BigAutoField(primary_key=True)
    name = models.TextField(db_index=True)


class WantedItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["entity", "item"], name="entity_need_item"
            )
        ]


# class ProposedItem(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     # Typically includes user as well to record who suggested it.
#     # Name is only necessary if Item does not exist?? Or should we just create the item?
#     # I'd rather not in case of NSFW
#     name = models.TextField(blank=True, null=True)
#     item = models.ForeignKey(Item, on_delete=models.CASCADE)
#     entity = models.ForeignKey(Entity, on_delete=models.CASCADE)


class ProposedItemArray(models.Model):
    id = models.BigAutoField(primary_key=True)
    # Typically includes user as well to record who suggested it.
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    items = ArrayField(models.BigIntegerField(), size=1000000)
    # Name is only necessary if Item does not exist?? Or should we just create the item?
    # I'd rather not in case of NSFW
    names = ArrayField(models.TextField(), size=10000000)
