"""Retrieve annotated data from BigQuery."""
from google.cloud import bigquery  # pylint: disable=import-error

from linalgo.annotate.models import Annotation, Annotator, Document, Task
from linalgo.annotate.utils import SoftDeleteSet


class BQClient:
    """Retrieve annotated data from BigQuery.

    Parameters
    ----------
    task_id: str
        The id of the task to retrieve.
    """

    def __init__(self, task_id, project=None):
        self.client = bigquery.Client(project=project)
        self.task_id = task_id

    def _get_query_data(self, query):
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter(
                    "task_id", "STRING", self.task_id),
            ]
        )
        job = self.client.query(query, job_config=job_config)
        return job.result()

    def get_annotations(self):
        """Retrieve all the annotations for the task."""
        prefix = "linalgo-infra.linhub_prod.public_"
        query = (
            'SELECT la.* '
            f'FROM `{prefix}linhub_corpus` lc '
            f'JOIN `{prefix}linhub_task_corpora` ltc ON ltc.corpus_id = lc.id '
            f'LEFT JOIN `{prefix}linhub_annotation` la ON la.task_id = ltc.task_id '
            'WHERE ltc.task_id = @task_id;'
        )
        rows = self._get_query_data(query)
        return SoftDeleteSet(Annotation.from_bq_row(row) for row in rows)

    def get_documents(self):
        """Retrieve all the documents for the task."""
        prefix = "linalgo-infra.linhub_prod.public_"
        query = (
            'SELECT ld.* '
            f'FROM `{prefix}linhub_document` ld '
            f'JOIN `{prefix}linhub_corpus` lc on lc.id = ld.corpus_id '
            f'JOIN `{prefix}linhub_task_corpora` ltc ON ltc.corpus_id = lc.id '
            'WHERE ltc.task_id = @task_id;'
        )
        rows = self._get_query_data(query)
        return SoftDeleteSet(Document.from_bq_row(row) for row in rows)

    def get_annotators(self):
        """Retrieve all the annotators of a task"""
        prefix = "linalgo-infra.linhub_prod.public_"
        query = (
            'SELECT * '
            f'FROM `{prefix}linhub_annotator` la '
            f'JOIN `{prefix}linhub_task_annotators`lta on lta.annotator_id = la.id '
            'WHERE lta.task_id = @task_id;'
        )
        rows = self._get_query_data(query)
        return [Annotator.from_bq_row(row) for row in rows]

    def get_task(self):
        """Return a task from BigQuery."""
        print("Fetching documents...", end='')
        documents = self.get_documents()
        print("OK.")
        print("Fetching annotations...", end='')
        annotations = self.get_annotations()
        print("OK")
        print("Fetching annotators...", end='')
        annotators = self.get_annotators()
        print("OK.")
        return Task(
            id=list(annotations)[0].task.id,
            annotators=annotators,
            documents=documents,
            annotations=annotations,
            corpora=set(doc.corpus for doc in documents)
        )


__all__ = ['BQClient']
