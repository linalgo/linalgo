import json
import uuid
from IPython.display import HTML

from linalgo.annotate import Document
from linalgo.annotate.serializers import AnnotationSerializer


def init():
    js = """
<style>

</style>
<script type="text/javascript" src="https://storage.googleapis.com/linhub.linalgo.com/linalgo.2.umd.js"></script>
<script type="text/javascript">
    function annotate(selector, annotations) {
        const Annotator = window["@linalgo/annotate-core"].Annotator
        const doc = document.querySelector(selector);
        const annotator = new Annotator(doc);
        for (annotation of annotations) {
            annotator.showAnnotation(annotation);
            const el = document.querySelector(`[id='${annotation.id}']`);
            el.onclick = function() { alert(JSON.stringify(annotation.body, null, 2)); };
        }
    }
</script>
<div style="font-style: italic;">Success!</div>
"""
    return HTML(js)


def display(doc: Document):
    doc_id = uuid.uuid4()
    html_doc = (
        f"<div class='doc{doc_id.hex}'>"
        f'{doc.content}'
        '</div>\n'
    )
    seralizer = AnnotationSerializer(doc.annotations)
    data = json.dumps(seralizer.serialize())
    javascript_code = (
        '<script type="text/javascript">\n'
        f"  annotate('.doc{doc_id.hex}', {data});\n"
        "</script>\n"
    )
    return HTML(html_doc + javascript_code)
