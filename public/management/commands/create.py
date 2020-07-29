from timeit import default_timer
import os
from random import sample

from django.conf import settings
from django.core.management.base import BaseCommand

from public.models import (
    ProposedItemArray, WantedItem, Entity, Item, ItemWithIndex
)


class Command(BaseCommand):
    help = (
        "Generates test data of english dict"
    )
    requires_migrations_checks = True

    def handle(self, *args, **options):
        # Check if words_alpha.txt exists
        path_to_dictionary = os.path.join(settings.BASE_DIR, "words_alpha.txt")
        if not os.path.exists(path_to_dictionary):
            import zipfile
            try:
                with zipfile.ZipFile(path_to_dictionary[:-3] + "zip", "r") as zip_ref:
                    zip_ref.extractall(settings.BASE_DIR)
            except FileNotFoundError as e:
                raise FileNotFoundError(f"You must include the zip file of the English"
                                        f" dictionary in the BASE_DIR, specified:\n{e}.")

        def load_words() -> set:
            """370099 words in the set"""
            with open("words_alpha.txt") as file:
                valid_words = set(file.read().split())
            return valid_words
        print("creating")
        words = [x.lower() for x in load_words()]

        blah = [Item(name=x) for x in words]
        Item.objects.bulk_create(blah, batch_size=20000)

        print("Timing filter")
        ItemWithIndex.objects.bulk_create([ItemWithIndex(name=x) for x in words])

        def timing(model, n):
            times = []
            iterations = 1000
            for x in range(iterations):
                # Get random words to filter on... maybe 100 and 1000 per
                sampled = sample(words, k=n)
                start = default_timer()
                bool(model.objects.filter(name__in=sampled))
                end = default_timer()
                times.append(end - start)
            return sum(times) / iterations

        print(f"Timing for 100: {timing(Item, 100)}")
        print(f"Timing for 1000: {timing(Item, 1000)}")
        print(f"Timing for 10000: {timing(Item, 10000)}")
        print(f"Timing for 100 w/ Index: {timing(ItemWithIndex, 100)}")
        print(f"Timing for 1000 w/ Index: {timing(ItemWithIndex, 1000)}")
        print(f"Timing for 10000 w/ Index: {timing(ItemWithIndex, 10000)}")

        # print("Queryset explain 100:", Item.objects.filter(name__in=sample(words, k=100)).explain(analyze=True))
        # print("Queryset explain 1000:", Item.objects.filter(name__in=sample(words, k=1000)).explain(analyze=True))
        # print("Queryset explain 10000:", Item.objects.filter(name__in=sample(words, k=10000)).explain(analyze=True))
        # print("Queryset explain 100 w/ Index:", ItemWithIndex.objects.filter(name__in=sample(words, k=100)).explain(analyze=True))
        # print("Queryset explain 1000 w/ Index:", ItemWithIndex.objects.filter(name__in=sample(words, k=1000)).explain(analyze=True))
        # print("Queryset explain 10000 w/ Index:", ItemWithIndex.objects.filter(name__in=sample(words, k=10000)).explain(analyze=True))

        print("Creating test data")
        Entity.objects.bulk_create([Entity() for _ in range(1000)])
        entity = Entity.objects.first()

        items = Item.objects.all()[:100]
        for x in items:
            WantedItem.objects.create(entity=entity, item=x)

        # Existing Items a part of Entity that shouldn't be added since already a part of Entity:
        # Tests UniqueConstraint.
        proposed_items = [x.id for x in items[50:100]]  # 50 items
        # Items that exist but aren't a part of Entity... well about to be.
        proposed_items += [x.id for x in items[200:300]]  # 100 items

        # Deleted items for the purposes of creating them as Item objects.
        lost_items = Item.objects.all()[1000:1100]
        lost_items = [x.name for x in lost_items]

        # Items that the user claims don't exist but actually do.
        # This can be because the merging process happens after a different
        # merge process creates an item
        user_new_system_old_items = [x.name for x in Item.objects.all()[2000:2100]]
        lost_items += user_new_system_old_items

        assert len(set(proposed_items)) == len(proposed_items)
        assert len(set(lost_items)) == len(lost_items)

        proposed = ProposedItemArray.objects.create(items=proposed_items, names=lost_items, entity=entity)
        print("End of creation")

        print("Beginning merge -- assuming staff approved")
        # First create the new items that already exist in Item
        WantedItem.objects.bulk_create([WantedItem(item_id=x, entity=entity) for x in proposed.items],
                                       ignore_conflicts=True)
        # Check for any existing items in "proposed new items"
        # Can happen when a new item shows up from a different merge but didn't update the array here
        proposed_names = set(proposed.names)
        existing_name_item_objs = Item.objects.filter(name__in=proposed_names)
        WantedItem.objects.bulk_create([WantedItem(item=item, entity=entity) for item in existing_name_item_objs],
                                       ignore_conflicts=True)

        # Finally create the rest of the items
        try:
            non_existing_names = proposed_names.difference({x.name for x in existing_name_item_objs})
            # Because we're using PostgreSQL, we get the pks
            items = Item.objects.bulk_create([Item(name=x) for x in non_existing_names],
                                             ignore_conflicts=True)
            WantedItem.objects.bulk_create([WantedItem(item=item, entity=entity) for item in items])
        except AttributeError:
            # In case proposed_names is empty... although I guess we should've handled this beforehand.....
            raise Exception("It should've been a set. The name/non-existant items array must've been empty.")
