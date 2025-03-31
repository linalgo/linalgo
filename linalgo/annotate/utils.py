"""A collection of utilities."""
import collections.abc


class SoftDeleteSet(collections.abc.MutableSet):
    """
    A set-like collection that supports soft deletion.

    Items added to the set are initially active. When an item is
    'removed' or 'discarded', it is marked as deleted but remains
    internally.

    Iteration, length calculation (`len`), and membership testing (`in`)
    only consider active items.
    """

    def __init__(self, iterable=None):
        """
        Initialize the SoftDeleteSet.

        Parameters
        ----------
        iterable: (optional)
            An iterable to initialize the set with. Duplicate items are ignored.
        """
        self._data = {}
        if iterable is not None:
            for value in iterable:
                self.add(value)

    def add(self, value):
        """
        Add an item to the set.

        If the item was previously deleted, it is marked as active again.
        If the item is already active, this operation has no effect.
        """
        self._data[value] = True  # Mark as active (or reactivate)

    def discard(self, value):
        """Remove an item from the set if it is currently active (soft delete).

        Does nothing if the item is not found or already deleted.

        Parameters
        ----------
        item:
            The item to discard
        """
        if value in self._data:
            self._data[value] = False

    def remove(self, value):
        """Remove an item from the set (soft delete).

        Parameters
        ----------
        item:
            The value to remove

        Raises
        ------
            KeyError: If the item is not found in the set or is already deleted.
        """
        if value in self and self._data[value]:
            self._data[value] = False
        else:
            raise KeyError(f"Item '{value}' not found in active set elements.")

    def __contains__(self, item):
        """Check if an item is currently active in the set."""
        return item in self._data and self._data[item] is True

    def __len__(self):
        """Return the number of active items in the set."""
        return sum(1 for status in self._data.values() if status)

    def __iter__(self):
        """Return an iterator over the active items in the set."""
        yield from (item for item, status in self._data.items() if status)

    def __repr__(self):
        """Return a string representation of the set (showing active items)."""
        active_items = set(self)
        return f"{self.__class__.__name__}({active_items!r})"

    def __str__(self):
        """Return a user-friendly string representation (showing active items)."""
        active_items = set(self)
        return str(active_items)
