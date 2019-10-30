import numpy as np
import pandas as pd

from .client import AssignmentStatus


class AnnotatorNotFound(Exception):
    pass


class NotEnoughReviews(Exception):
    pass


class Scheduler:

    def __init__(self, task, schedule):
        self.task = task
        self.schedule = schedule

    def random_review(self, reviewer_id, reviewee_id, n=None):
        """
        Parameters
        ----------
        reviewer_id: uuid
            The uuid of the reviewer
        reviewee_id: uuid
            The uuid of the reviewee
        n: int
            The number of documents to review

        Return
        ------
        A set of documents to review
        """

        if (reviewer_id not in {a.id for a in self.task.annotators} or
            reviewee_id not in {a.id for a in self.task.annotators}):
            raise AnnotatorNotFound()
        reviewer_idx = self.schedule['annotator'] == reviewer_id
        reviewee_idx = self.schedule['annotator'] == reviewee_id
        seen_idx = self.schedule['status'] == AssignmentStatus.COMPLETED.value
        pending_idx = self.schedule['status'] == AssignmentStatus.ASSIGNED.value

        idx = reviewer_idx & (seen_idx | pending_idx)
        reviewer_docs = set(self.schedule.loc[idx, 'document'])
        idx = reviewee_idx & seen_idx
        reviewee_docs = set(self.schedule.loc[idx, 'document'])

        pool = list(reviewee_docs - reviewer_docs)
        if n is not None:
            if n > len(pool):
                print(pool)
                raise NotEnoughReviews()
            return set(np.random.choice(pool, size=n, replace=False))
        return pool

    def random_assign(self, assignee_id, n):
        """

        Parameters
        ----------

        assignee_id: uuid
            The uuid of the annotator
        n: int
            the number of documents

        Return
        ------
        A set of documents to assign
        """

        if assignee_id not in {a.id for a in self.task.annotators}:
            raise AnnotatorNotFound(
                '{} is not a known annotator'.format(assignee_id))

        all_docs = set(doc.id for doc in self.task.documents)
        all_seen_docs = set()
        for annotation in self.task.annotations:
            all_seen_docs.add(annotation.to_json()['document'])
        all_new_docs = all_docs - all_seen_docs

        assignee_idx = self.schedule['annotator'] == assignee_id
        seen_idx = self.schedule['status'] == AssignmentStatus.COMPLETED.value
        pending_idx = self.schedule['status'] == AssignmentStatus.ASSIGNED.value

        idx = assignee_idx & (seen_idx | pending_idx)
        assignee_docs = set(self.schedule.loc[idx, 'document'])

        pool = list(all_new_docs - assignee_docs)
        if n > len(pool):
            print(pool)
            raise NotEnoughReviews()
        return set(np.random.choice(pool, size=n, replace=False))

