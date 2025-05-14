Home
=======

Linalgo is a Python module to help Machine Learning team create and curate 
datasets for Natural Language Processing. It tries to follow
the W3C `Web Annotation Data Model <https://www.w3.org/TR/annotation-model/>`_ and
to provides a powerful system to add metadata to most commonly used text and
image formats: TXT, PDF, HTML, etc.

Installation
============

You can install linalgo using pip::

    pip install linalgo

For other options, see :ref:`install_page`.

Getting started
===============

Examples
--------

Examples will be available in the `examples/` folder.

Tutorials
---------

**Getting task data**

.. code-block:: python

    from linalgo.client import LinalgoClient
   
    client_id = '<YOUR_CLIENT_ID_HERE>'
    client_secret = '<YOUR_SECRET_HERE>'
    linalgo_client = LinalgoClient(client_id, client_secret)

**Training a binary classifier**

.. code-block:: python

    from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipelin

    task_id = 1
    tasks = linalgo_client.get_task(task_id)
    
    label = 4
    docs, labels = task.transform(target='binary',  label=label)
    
    X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.33, random_state=42)
    
    text_clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', LogisticRegression()),
    ])
    
    text_clf.fit(X_train, y_train)  
    predicted = text_clf.predict(X_test)


.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`