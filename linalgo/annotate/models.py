"""Definition of the main models."""
import copy
from enum import Enum
from datetime import datetime
from typing import Dict, Iterable, List, Union
import json
import uuid

from linalgo.annotate.bounding_box import BoundingBox, Vertex


Selector = Union[BoundingBox]


class NoFactoryError(Exception):
    """No Factory Error."""


class XPathSelector:
    """W3C XPathSelector.

    See: `https://www.w3.org/TR/annotation-model/#xpath-selector`

    Attributes
    ----------
    start_container : str
        The path to the start container.
    end_container : str
        The path to the end container.
    start_offset : int
        The offset of the start container.
    end_offset : int
        The offset of the end container.
    """

    def __init__(
        self,
        start_container: str = '/',
        end_container: str = '/',
        start_offset: int = None,
        end_offset: int = None
    ):
        self.start_container = start_container
        self.end_container = end_container
        self.start_offset = start_offset
        self.end_offset = end_offset


class SelectorFactory:
    """A class to create `Selector` objects from different formats."""

    @staticmethod
    def factory(d: Dict):
        """Factory method for `Selector`.

        Parameters
        ----------
        d : Selector | dict

        Returns
        -------
        Selector
            The created `Selector` object.
        """
        if isinstance(d, dict):
            if d == {}:
                return d
            if 'x' in d:
                v = Vertex(d['x'], d['y'])
                return BoundingBox.from_vertex(
                    v, height=d['height'], width=d['width'])
            if 'startOffset' in d:
                return XPathSelector(
                    start_container=d['startContainer'],
                    end_container=d['endContainer'],
                    start_offset=d['startOffset'],
                    end_offset=d['endOffset']
                )
        if isinstance(d, XPathSelector):
            return d
        if isinstance(d, BoundingBox):
            return d
        raise NoFactoryError(f"No factory found for {type(d)}")


class TargetFactory:
    """A class to create W3C Target objects from different formats."""

    @staticmethod
    def factory(data):
        """Factory method for W3C Target."""
        if data is None:
            return Target(selector=[XPathSelector()])
        if isinstance(data, Target):
            return data
        if isinstance(data, str):
            d = json.loads(data.replace("\'", "\""))
            return TargetFactory.from_dict(d)
        if isinstance(data, dict):
            return TargetFactory.from_dict(data)
        raise NotImplementedError(f'No factory found for type {type(data)}')

    @staticmethod
    def from_dict(d: Dict):
        """Creates a W3C target from a dictionary."""
        if d == {}:
            return Target(selector=[])
        return Target(
            source=Document.factory(d['source']),
            selector=[SelectorFactory.factory(s) for s in d['selector']]
        )


class Target(TargetFactory):
    """W3C Target object.

    See: https://www.w3.org/TR/annotation-model/#bodies-and-targets

    Attributes
    ----------
    source : Document
        The document that is being annotated.
    selector : Selector
        The selector that is being used to annotate the document.
    """

    def __init__(
        self,
        source: 'Document' = None,
        selector: Iterable[Selector] = None
    ):
        self.source = source
        if selector is None:
            selector = []
        self.selector = [SelectorFactory.factory(s) for s in selector]

    def __repr__(self):
        return str(self.selector)

    def copy(self):
        """Return a copy of the target."""
        return Target(
            source=self.source,
            selector=[copy.deepcopy(s) for s in self.selector])


class RegistryMixin:
    """The registry makes sure that each object has a unique id."""

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        """Return a unique object based on the id."""
        unique_id = kwargs.get('unique_id', str(uuid.uuid4()))
        unique_id = kwargs.get('id', unique_id)
        if not hasattr(cls, '_registry'):
            cls._registry = {}
        if unique_id in cls._registry:
            return cls._registry[unique_id]
        obj = super().__new__(cls)
        obj.id = unique_id
        cls._registry[unique_id] = obj
        return obj

    def get(self, name, value):
        """Set the value of the attribute if it is not None.

        Parameters
        ----------
        name : str
            The name of the attribute.
        value : any
            The value to set.

        Returns
        -------
        any
            The value of the attribute.
        """
        if value in (None, [], set()):
            if hasattr(self, name):
                if getattr(self, name) not in (None, [], set()):
                    value = getattr(self, name)
        return value


class FromIdFactoryMixin:
    """Enable object instanciation using just a unique id.

    In order to sync the objects between the remote repo and the local
    version, object of the same class that share the same unique ID should
    point to the same instance. This is achieved by having a global registry
    that enforces the singleton pattern for each class/id combination.
    """

    @classmethod
    def factory(cls, arg):
        """The factory returning the unique object based on the id."""
        if arg is None:
            return cls(unique_id=str(uuid.uuid4()))
        if isinstance(arg, cls):
            return arg
        if isinstance(arg, str):
            return cls(unique_id=arg)
        raise NoFactoryError(f'No factory method found for type {type(arg)}')


class AnnotationFactory:
    """A Factory to create Annotation objects from different formats."""

    @staticmethod
    def from_dict(d: Dict):
        """Creates a W3C Web Annotation from a dictionary."""
        return Annotation(
            unique_id=d['id'],
            entity=Entity(unique_id=d['entity']),
            body=d['body'],
            annotator=Annotator(unique_id=d['annotator']),
            document=Document(unique_id=d['document']),
            task=Task(unique_id=d['task']),
            target=Target.factory(d['target']),
            created=d['created']
        )

    @staticmethod
    def from_bq_row(row):
        """Create a W3C Annotation from a BigQuery row."""
        return Annotation(
            unique_id=row.id,
            entity=row.entity_id,
            document=row.document_id,
            body=row.body,
            annotator=row.annotator_id,
            task=row.task_id,
            created=row.created,
            target=row.target
        )


class Annotation(RegistryMixin, FromIdFactoryMixin, AnnotationFactory):
    # pylint: disable=too-many-instance-attributes
    """
    Annotation class compatible with the W3C annotation data model.

    Attributes
    ----------
    entity: Entity
        The entity that is being annotated
    document: Document
        The document that is being annotated
    body: str
        The body of the annotation
    annotator: Annotator
        The annotator that created the annotation
    task: Task
        The task that the annotation belongs to
    created: datetime
        The date and time the annotation was created
    target: Target
        The target of the annotation
    score: float
        The score of the annotation
    auto_track: bool
        Whether to automatically track the annotation in the document
    """

    def __init__(
        self,
        entity: 'Entity' = None,
        document: 'Document' = None,
        body: str = None,
        annotator: 'Annotator' = None,
        task: 'Task' = None,
        created=None,
        target: Target = None,
        score: float = None,
        auto_track=True,
        start: int = None,
        end: int = None,
        **kwargs  # pylint: disable=unused-argument
    ):
        if entity is None:
            entity = kwargs.get('entity_id')
        if task is None:
            task = kwargs.get('task_id')
        if annotator is None:
            annotator = kwargs.get('annotator_id')
        if document is None:
            document = kwargs.get('document_id')
        if created is None:
            created = datetime.now()
        elif isinstance(created, str):
            created = datetime.fromisoformat(created.replace('Z', '+00:00'))
        self.entity = self.get('entity', Entity.factory(entity))
        self.score = self.get('score', score)
        self.body = self.get('body', body)
        self.task = self.get('task', Task.factory(task))
        self.annotator = self.get(
            'annotator', Annotator.factory(annotator))
        self.document = self.get(
            'document', Document.factory(document))
        if auto_track:
            self.document.annotations.add(self)
        self.target = self.get('target', TargetFactory.factory(target))
        if start is not None:
            self.target.selector[0].start_offset = start
        if end is not None:
            self.target.selector[0].end_offset = end
        self.created = self.get('created', created)

    def __repr__(self):
        return f'Annotation::{self.id}'

    @property
    def start(self):
        """Return the start offset of the annotation."""
        return self.target.selector[0].start_offset

    @property
    def end(self):
        """Return the end offset of the annotation."""
        return self.target.selector[0].end_offset

    def get_context(self, context_len):
        """Returns the context of the annotation.

        Parameters
        ----------
        context_len : int
            The length of the context to return.
        """
        xpath = self.target.selector[0]
        start = max(0, xpath.start_offset - context_len)
        end = min(xpath.end_offset + context_len, len(self.document.content))
        return self.document.content[start:end]

    def copy(self):
        """Returns a copy of the annotation with a different unique id."""
        target = self.target.copy()
        return Annotation(
            unique_id=str(uuid.uuid4()),
            entity=self.entity,
            document=self.document,
            task=self.task,
            target=target,
            body=self.body,
            annotator=self.annotator,
            score=self.score
        )


class AnnotatorFactory:
    """A factory class to create Annotator objects from different formats."""

    @staticmethod
    def from_dict(d):
        """Creates a Annotator from a dictionary."""
        return Annotator(
            unique_id=d['id'],
            name=d['name'],
            owner=d['owner']
        )


class Annotator(RegistryMixin, FromIdFactoryMixin, AnnotatorFactory):
    """The Annotator class can create, delete or modify Annotations.

    Parameters
    ----------
    name : str
        The name of the annotator
    model: str
        The model to use for the annotator
    task : Task
        The task that the annotator is assigned to
    entity_id : int
        The entity that the annotator is assigned to
    threshold : float
        The threshold for the annotator
    owner : str
        The owner of the annotator
    """

    def __init__(
        self,
        name: str = None,
        model=None,
        task: 'Task' = None,
        entity_id=None,
        threshold: float = 0,
        owner=None,
        **kwargs  # pylint: disable=unused-argument
    ):
        self.name = self.get('name', name)
        self.task = self.get('task', Task.factory(task))
        self.owner = self.get('owner', owner)
        self.model = self.get('model', model or 'MACHINE')
        self.entity_id = self.get('entity_id', entity_id)
        self.threshold = self.get('threshold', threshold)

    def __repr__(self):
        return f'Annotator::{self.name or self.id}'

    def assign_task(self, task):
        """Assign a task to the annotator.

        Parameters
        ----------
        task : Task
            The task to assign to the annotator.
        """
        self.task = task

    def _get_annotation(self, document):
        score = self.model.decision_function([document.content])[0]
        if score >= self.threshold:
            label = self.entity_id
        else:
            label = 1  # Viewed
        annotation = Annotation(
            entity_id=label,
            score=score,
            text=document.content,
            annotator=self.id,
            task_id=self.task.id,
            document_id=document.id
        )
        return annotation

    def annotate(self, document):
        """Annotate a document.

        Parameters
        ----------
        document : Document
            The document to annotate.
        """
        annotation = self._get_annotation(document)
        if annotation is not None:
            self.task.annotations.append(annotation)
            document.annotations.add(annotation)
        return annotation


class CorpusFactory(FromIdFactoryMixin):
    """A factory class to create ref::`Corpus` objects from different formats."""

    @staticmethod
    def from_dict(d):
        """Creates a Corpus from a dictionary."""
        return Corpus(
            unique_id=d['id'],
            name=d['name'],
            description=d['description'],
        )


class Corpus(RegistryMixin, CorpusFactory):
    """A Corpus is a collection of documents.

    Parameters
    ----------
    name : str
        The name of the corpus
    description : str
        The description of the corpus
    documents : Iterable[Document]
        The documents that are in the corpus
    """

    def __init__(
        self,
        name: str = None,
        description: str = None,
        documents: Iterable['Document'] = None,
        **kwargs  # pylint: disable=unused-argument
    ):
        self.name = self.get('name', name)
        self.description = self.get('description', description)
        if documents is None:
            documents = set()
        self.documents = self.get(
            'documents', [Document.factory(d, corpus=self) for d in documents])

    def __repr__(self):
        return f'Corpus::{self.name or self.id}'


class DocumentFactory(FromIdFactoryMixin):
    """A factory class to create ref::`Document` objects from different formats."""

    @classmethod
    def factory(cls, arg, **kwargs):
        instance = super().factory(arg)
        if 'corpus' in kwargs:
            instance.corpus = kwargs['corpus']
        return instance

    @staticmethod
    def from_dict(d):
        """Creates a Document from a dictionary."""
        return Document(
            unique_id=d['id'],
            uri=d['uri'],
            content=d['content'],
            corpus=Corpus(d['corpus'])
        )

    @staticmethod
    def from_bq_row(row):
        """Creates a Document from a BigQuery row."""
        return Document(
            unique_id=row.id,
            uri=row.uri,
            content=row.content,
            corpus=row.corpus_id
        )


class Document(RegistryMixin, DocumentFactory):
    """A Document is the base object that will receive annotations.

    Parameters
    ----------
    content : str
        The content of the document.
    uri : str
        The URI of the document.
    corpus : Corpus
        The corpus that the document belongs to.
    """

    def __init__(
        self,
        content: str = None,
        uri: str = None,
        corpus: Corpus = None,
        **kwargs  # pylint: disable=unused-argument
    ):
        self.uri = self.get('uri', uri)
        self.content = self.get('content', content)
        self.corpus = self.get('corpus', Corpus.factory(corpus))
        self.annotations = self.get('annotations', set())

    @property
    def entities(self):
        """Return the entities in the document."""
        return list(set(a.entity for a in self.annotations))

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f'Document::{self.id}'


class EntityFactory:
    """A factory class to create ref::`Entity` objects from different formats."""

    @staticmethod
    def from_dict(d: Dict):
        """Creates a Entity from a dictionary."""
        return Entity(
            unique_id=d['id'],
            name=d['title'],
            color=d['color']
        )


class Entity(RegistryMixin, FromIdFactoryMixin, EntityFactory):
    """An Entity define the type of an ref::`Annotation`.

    Parameters
    ----------
    name : str
        The name of the entity
    color : str
        The color of the entity
    """

    def __init__(
        self,
        name: str = None,
        color: str = None,
        **kwargs  # pylint: disable=unused-argument
    ):
        self.name = self.get('name', name)
        self.color = self.get('color', color)

    def __repr__(self):
        return f'Entity::{self.name or self.id}'


class TaskFactory(FromIdFactoryMixin):
    """A factory class to create Task objects from different formats."""

    @staticmethod
    def from_dict(d):
        """Creates a Task from a dictionary."""
        return Task(
            unique_id=d['id'],
            name=d['name'],
            description=d['description'],
            entities=[Entity(e) for e in d['entities']],
            corpora=[Corpus.factory(c) for c in d['corpora']],
            annotators=[Annotator(a) for a in d['annotators']],
        )


class Task(RegistryMixin, TaskFactory):
    """Creates a Task object.

    A `Task` contains is the main entry point for a project and has information
    on `Entities`, `Corpora` and `Annotators`.

    Parameters
    ----------
    name : str
        The name of the task
    description : str
        The description of the task
    entities : List[Entity]
        The entities that are being annotated
    corpora : List[Corpus]
        The corpora that are being annotated
    annotators : List[Annotator]
        The annotators that are being used to annotate the corpora
    documents : List[Document]
        The documents that are being annotated
    annotations: Iterable[Annotation]
        The annotations that are being annotated
    """

    def __init__(
        self,
        name: str = None,
        description: str = None,
        entities: List[Entity] = None,
        corpora: List[Corpus] = None,
        annotators: List[Annotator] = None,
        documents: List[Document] = None,
        annotations: Iterable[Annotation] = None,
        is_private: bool = True,
        task_type: str = 'custom',
        labelling_app_url: str = None,
        **kwargs  # pylint: disable=unused-argument
    ):
        if entities is None:
            entities = []
        if corpora is None:
            corpora = []
        if annotators is None:
            annotators = []
        if documents is None:
            documents = set()
        if annotations is None:
            annotations = []
        self.name = self.get('name', name)
        self.description = self.get('description', description)
        self.entities = self.get(
            'entities', [Entity.factory(e) for e in entities])
        self.corpora = self.get(
            'corpora', [Corpus.factory(c) for c in corpora])
        self.annotators = self.get(
            'annotators', [Annotator.factory(a) for a in annotators])
        self.annotations = self.get(
            'annotations', set(Annotation.factory(a) for a in annotations))
        self.documents = self.get(
            'documents', set(Document.factory(d) for d in documents))
        self.is_private = is_private
        self.task_type  = task_type
        self.labelling_app_url = labelling_app_url

    def __repr__(self):
        return f'Task::{str(self.id)}'

    def add_annotation(self, annotation: Annotation):
        """Add an annotation to the task."""
        self.annotations.add(annotation)

    def add_document(self, document: Document):
        """Add a document to the task."""
        self.documents.add(document)


class Organization(RegistryMixin, FromIdFactoryMixin):
    # pylint: disable=too-many-instance-attributes
    """An `Organization` is the entity that owns a tasks and datasets.

    Parameters
    ----------
    name : str
        The name of the organization
    avatar : str
        The avatar of the organization
    slug : str
        The slug of the organization
    description : str
        The description of the organization
    website : str
        The website of the organization
    email : str
        The email of the organization
    location : str
        The location of the organization
    individual : bool
        Whether the organization is an individual or not
    created : str
        The date and time the organization was created
    """

    def __init__(
        self,
        name: str,
        avatar: str,
        slug: str,
        description: str,
        website: str,
        email: str,
        location: str,
        individual: bool,
        created: str,
        **kwargs  # pylint: disable=unused-argument
    ):
        self.name = self.get('name', name)
        self.avatar = self.get('avatar', avatar)
        self.slug = self.get('slug', slug)
        self.description = self.get('description', description)
        self.website = self.get('website', website)
        self.email = self.get('email', email)
        self.location = self.get('location', location)
        self.individual = self.get('individual', individual)
        self.created = self.get('created', created)

    def __repr__(self):
        return f"{self.id}::{self.name}"


class DocumentStatus(Enum):
    """The status of the document."""
    ASSIGNED = 'A'
    COMPLETED = 'C'


class ScheduleType(Enum):
    """The type of the schedule."""
    REVIEW = 'R'
    ANNOTATE = 'A'


class Schedule:
    # pylint: disable=too-many-instance-attributes
    """A Schedule defines who should review what.

    A Review can be an ref::`Annotator` reviewing a ref::`Document`, or it could
    be an ref::`Annotator` reviewing an ref::`Annotation`.

    Parameters
    ----------
    status : str
        The status of the schedule
    schedule_type : str
        The type of the schedule
    priority : float
        The priority of the schedule
    timestamp : str
        The timestamp of the schedule
    document : Document
        The document that is being annotated
    annotator : Annotator
        The annotator that is being used to annotate the document
    task : Task
        The task that is being annotated
    reviewee : Annotator
        The annotator that is reviewing the document
    """

    def __init__(
        self,
        status: str,
        schedule_type: str,
        priority: float,
        timestamp: str,
        document: Document,
        annotator: Annotator,
        task: Task,
        reviewee: Annotator,
        **kwargs  # pylint: disable=unused-argument
    ):
        self.status = DocumentStatus(status)
        self.schedule_type = ScheduleType(schedule_type)
        self.priority = priority
        self.timestamp = timestamp
        self.document = Document(document)
        self.annotator = Annotator(annotator)
        self.task = Task(task)
        self.reviewee = Annotator(reviewee)

    def __repr__(self) -> str:
        return f'Schedule::{self.schedule_type}::{self.status}'


__all__ = [
    'Annotation', 'Annotator', 'Corpus', 'Document', 'Entity', 'Task',
    'Organization', 'DocumentStatus', 'ScheduleType', 'Schedule'
]
