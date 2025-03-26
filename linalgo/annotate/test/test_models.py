# pylint: skip-file
import unittest

from linalgo.annotate.models import Annotation, Document
from .fixtures import ANNOTATIONS, DOCUMENTS


class TestModels(unittest.TestCase):

    def test_unique_id_mixin(self):
        a1 = Annotation(id='same', entity='abcd')
        a2 = Annotation(id='same', entity='efgh')
        self.assertEqual(a1, a2)

    def test_create_annotation_from_dict(self):
        fixture = ANNOTATIONS[0]
        a = Annotation.from_dict(fixture)
        self.assertEqual(fixture['document'], a.document.id)

    def test_override_annotation(self):
        fixture = ANNOTATIONS[0]
        a1 = Annotation(
            unique_id=fixture['id'],
            entity=fixture['entity'],
            document=fixture['document']
        )
        a2 = Annotation.from_dict(fixture)
        self.assertEqual(a1, a2)

    def test_document(self):
        doc_fixture = DOCUMENTS[0]
        anno_fixture = ANNOTATIONS[0]
        doc = Document.from_dict(doc_fixture)
        anno = Annotation.from_dict(anno_fixture)
        self.assertEqual(doc, anno.document)

    def test_override_document(self):

        d1 = Document(id=1, content="plop")
        d2 = Document(id=1, uri="https://plop.plip")
        self.assertEqual(d1.content, "plop")
        self.assertEqual(d1.uri, "https://plop.plip")
        self.assertEqual(d1, d2)


if __name__ == '__main__':
    unittest.main()
