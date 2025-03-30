"""Serializers for linalgo models."""
from linalgo.annotate import models
from linalgo.annotate.bounding_box import BoundingBox


# pylint: disable=too-few-public-methods
class Serializer:
    """Base class for serializers."""

    def __init__(self, instance):
        self.instance = instance
        self.many = hasattr(instance, '__len__')

    @staticmethod
    def _serialize(instance):
        """Serialize the instance."""
        raise NotImplementedError

    def serialize(self):
        """Serialize the instance."""
        if self.many:
            return [self._serialize(i) for i in self.instance]
        return self._serialize(self.instance)


class BoundingBoxSerializer(Serializer):
    """Serializer for BoundingBox."""

    @staticmethod
    def _serialize(instance):
        s = {
            'vertex': instance.vertex,
            'height': instance.height,
            'width': instance.width
        }
        return s


class XPathSelectorSerializer(Serializer):
    """Serializer for XPathSelector."""

    @staticmethod
    def _serialize(instance):
        s = {
            'startContainer': instance.start_container,
            'endContainer': instance.end_container,
            'startOffset': instance.start_offset,
            'endOffset': instance.end_offset
        }
        return s


class NoSerializerFound(Exception):
    """No serializer was found for the given instance."""

    def __init__(self, instance):
        self.message = f"No serializer found for {type(instance)}"
        super().__init__(self.message)


class SelectorSerializerFactory:
    """Factory for creating serializers for selectors."""

    @staticmethod
    def create(instance):
        """Create a serializer for the given instance."""
        if isinstance(instance, BoundingBox):
            return BoundingBoxSerializer(instance)
        if isinstance(instance, models.XPathSelector):
            return XPathSelectorSerializer(instance)
        raise NoSerializerFound(instance)


class TargetSerializer(Serializer):
    """Serializer for Target."""

    @staticmethod
    def _serialize(instance):
        s = {'selector': [], 'source': None}
        if hasattr(instance.source, 'id'):
            s['source'] = instance.source.id
        for selector in instance.selector:
            serializer = SelectorSerializerFactory.create(selector)
            s['selector'].append(serializer.serialize())
        return s

class TaskSerializer(Serializer):
    """Serializer for Task."""

    @staticmethod
    def _serialize(instance: models.Task):
        entities = EntitySerializer(instance.entities).serialize()
        annotators = AnnotatorSerializer(instance.annotators).serialize()
        corpora = CorpusSerializer(instance.corpora).serialize()

        return {
            'name': instance.name,
            'description': instance.description,
            'entities': entities,
            'annotators': annotators,
            'corpora': corpora,
            'is_private': instance.is_private,
            'type': instance.task_type,
            'labelling_app_url': instance.labelling_app_url
        }


class AnnotatorSerializer(Serializer):
    """Serializer for Annotator."""

    @staticmethod
    def _serialize(instance: models.Annotator):
        return {
            'id': instance.id,
            'name': instance.name,
            'task': instance.task,
            'model': instance.model,
            'entity_id': instance.entity_id,
        }


class EntitySerializer(Serializer):
    """Serializer for Entity."""

    @staticmethod
    def _serialize(instance: models.Entity):
        return {
            'id': instance.id,
            'title': instance.name
        }


class AnnotationSerializer(Serializer):
    """Serializer for Annotation."""

    @staticmethod
    def _serialize(instance: models.Annotation):
        annotator_id = None
        if instance.annotator is not None:
            annotator_id = instance.annotator.id
        target = None
        if instance.target is not None:
            target_serializer = TargetSerializer(instance.target)
            target = target_serializer.serialize()
        s = {
            'id': instance.id,
            'task': instance.task.id,
            'entity': instance.entity.id,
            'body': instance.body or '',
            'annotator': annotator_id,
            'document': instance.document.id,
            'created': instance.created.strftime('%Y/%m/%d %H:%M:%S.%f'),
            'target': target
        }
        return s


class DocumentSerializer(Serializer):
    """Serializer for Document."""

    @staticmethod
    def _serialize(instance):
        return {
            'id': instance.id,
            'uri': instance.uri,
            'content': instance.content,
            'corpus_id': instance.corpus.id
        }


class CorpusSerializer(Serializer):
    """Serializer for Corpus."""

    @staticmethod
    def _serialize(instance: models.Corpus):
        s = DocumentSerializer(instance.documents)
        return {
            'id': instance.id,
            'name': instance.name,
            'description': instance.description,
            'documents': s.serialize()
        }
