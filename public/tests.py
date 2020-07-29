from django.test import TestCase
from .models import Item, Entity, WantedItem
from django.db.utils import IntegrityError
from django.db import transaction


class Blah(TestCase):
    def test_blah(self):
        """
        django.db.utils.IntegrityError: duplicate key value violates unique constraint "entity_need_item"
        DETAIL:  Key (entity_id, item_id)=(1, 1) already exists.

        Bulk Create upholds IntegrityError unless you ignore conflicts :)
        """
        e = Entity.objects.create()
        Item.objects.create(name="asdf")
        Item.objects.create(name="asdfasdf")
        WantedItem.objects.create(item=Item.objects.first(), entity=e)
        try:
            with transaction.atomic():
                WantedItem.objects.bulk_create([WantedItem(item=x, entity=e) for x in Item.objects.all()],
                                               ignore_conflicts=True)
        except IntegrityError:
            ...
        assert WantedItem.objects.count() == 2, WantedItem.objects.count()
