import numpy as np


class BaseBatchGenerator:
    """A generic base class for generating batches of data."""

    def generate_forever(self, items, batch_size, shuffle=True):
        """Return an generator that will forever generate batches from `items`.

        Args:
            items (list like): A list of items to generate batches from.
                `items` may represent a list of individual training steps (e.g.
                a list of `numpy` arrays) or a list of objects from which
                multiple training steps can be generated (e.g. a list of
                filenames). In the latter case users must override `generate_steps()`.
            batch_size (int): Desired batch size.

        Returns:
            generator.
        """
        item = items[:]  # copy so we can shuffle in place
        while True:
            if shuffle:
                np.random.shuffle(items)
            yield from self.generate_epoch(items, batch_size)
            
    def generate_epoch(self, items, batch_size):
        """Return an iterator that generates a single epoch (that is, a single
        pass over `items`).

        Args:
            items (list like): A list of items to generate batches from.
                `items` may represent a list of individual training steps (e.g.
                a list of `numpy` arrays) or a list of objects from which
                multiple training steps can be generated (e.g. a list of
                filenames). In the latter case users must override `generate_steps()`.
            batch_size (int): Desired batch size.

        Returns:
            generator.
        """
        steps = []
        for item in items:
            training_steps = self.generate_steps(item)
            steps.extend(training_steps)
            batches, remaining_steps = self.generate_batches(steps, batch_size)
            steps = remaining_steps
            yield from batches

    def generate_batches(self, steps, batch_size):
        """Return an iterator of batches given a list of training steps, batch
        size and number of batches in `steps`.

        Args:
            steps (list): A list of training steps generated by `generate_steps()`.
            batch_size (int): Desired batch size.
            n_batches (int): The calculated number of batches of size `batch_size`
                contained in `steps`.

        Returns:
            tuple: A generator of batches and list of steps not consumed (any
                leftover steps that couldn't be used to make a whole batch).
        """
        raise NotImplementedError

    def generate_steps(self, item):
        """Return a list of training steps represented by `item`.

        The default implementation assumes that each item in the list `items`
        passed to `generate_forever()` or `generate_batches()` is a single
        training step (instance). If this is not the case, users can override
        this method to generate a list of training steps from `item`.

        Args:
            item (object): A single training step or object from which multiple
                training steps can be generated.

        Returns:
            list. A list of training step(s) represented by `item`.
        """
        return [item]

    def batches_per_epoch(self, items, batch_size):
        """Return the number of batches that would be returned from

            `BaseBatchGenerator.generate_epoch(items, batch_size)`

        Note: this is done in a naive way that will accomodate any use case.
        The user should override this for efficiency when required.

        Args:
            items (list like): A list of items to generate batches from.
            batch_size (int): Desired batch size.

        Returns:
            int. The number of batches of size `batch_size` in a single epoch
                generated from `items`.
        """
        epoch = self.generate_epoch(items, batch_size)
        for i, batch in enumerate(epoch, start=1):
            pass
        return i
