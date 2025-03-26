# pylint: skip-file
import unittest

from linalgo.annotate.models import Annotation, Document, Task
from linalgo.annotate.transformers import Sequence2SequenceTransformer

class TestTransformers(unittest.TestCase):

    doc = Document(content="Hello, how are you?")

    annotations = [
        Annotation(body="g", document=doc, annotator='A1', start=0, end=5),
        Annotation(body="u", document=doc, annotator='A1', start=7, end=9),
        Annotation(body="u", document=doc, annotator='A1', start=11, end=13),
        Annotation(body="p", document=doc, annotator='A1', start=15, end=18),
        Annotation(body="g", document=doc, annotator='A2', start=0, end=5),
        Annotation(body="u", document=doc, annotator='A2', start=7, end=9),
        Annotation(body="u", document=doc, annotator='A2', start=11, end=13),
        Annotation(body="p", document=doc, annotator='A2', start=15, end=18),
        Annotation(body="x", document=doc, annotator='A3', start=0, end=5),
        Annotation(body="x", document=doc, annotator='A3', start=7, end=9),
        Annotation(body="x", document=doc, annotator='A3', start=11, end=13),
        Annotation(body="x", document=doc, annotator='A3', start=15, end=18),
        
    ]

    def test_sequence_to_sequence(self):

        def tokenize(text):
            idx = 0
            for token in text.split():
                yield idx, token
                idx += len(token) + 1
                
        task = Task(name="test")
        task.documents.append(self.doc)
        task.annotations.append(self.annotations)
        t = Sequence2SequenceTransformer(tokenize_fn=tokenize)
        in_seqs, out_seqs = t.transform(task)
        self.assertEqual(in_seqs, [self.doc.content.split()])
        self.assertEqual(out_seqs, [["g", "u", "u", "p"]])

