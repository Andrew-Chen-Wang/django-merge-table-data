# Django Merge Table Data

Created by Andrew Chen Wang

Created on 29 July 2020

This repository is dedicated to Donate Anything's proposed item migration to WantedItem model.

The purpose of this is to efficiently create probably thousands of items or hundreds of thousands of items efficiently.

However, there is a unique constraint applied.

There are two tests models: one uses an ArrayField for all items, the other is simply a simple merge of one table's data to the other... this is if I don't cut it out later on.

The first thing I'm gonna try and do is just trying and doing the merging. The second part comes in performance.

The problem with PostgreSQL's ArrayField  is that the user input can't be cleaned without checking an entire table I suppose. The problem with one proposed item being a new record is the amount of data being stored. Plus, the array field can't be ordered alphabetically.

Well... I guess it doesn't matter for proposed items, only the actual items.

---
### License

Licenced under the mIT license