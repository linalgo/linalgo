"""A collection of helper tools to visualize annotations in Jupyter notebooks."""
import json
import uuid
from IPython.display import HTML

from linalgo.annotate import Document
from linalgo.annotate.serializers import AnnotationSerializer


def init():
    """Initialize the display environment."""
    js = """
<style>
    .underline {
        border-bottom: 1px dotted grey;
        cursor: pointer;
    }
    .tooltip {
        display: none;
        background: #333;
        color: white;
        font-weight: bold;
        padding: 4px 8px;
        font-size: 13px;
        border-radius: 4px;
    }

    .tooltip[data-show] {
        display: block;
    }
</style>
<script type="text/javascript" src="https://storage.googleapis.com/linhub.linalgo.com/linalgo.2.umd.js"></script>
<script src="https://unpkg.com/@popperjs/core@2"></script>
<script type="text/javascript">
function annotate(selector, annotations) {
    const Annotator = window["@linalgo/annotate-core"].Annotator
    const doc = document.querySelector(`[id='${selector}']`);
    const annotator = new Annotator(doc);
    for (annotation of annotations) {
        annotator.showAnnotation(annotation);
        const el = document.querySelector(`[id='${annotation.id}']`);
        el.classList.add("underline");
        const node = document.createElement("pre");
        node.setAttribute("role", "tooltip");
        const textnode = document.createTextNode(JSON.stringify(annotation.body, null, 2));
        node.appendChild(textnode);
        node.classList.add("tooltip");
        el.appendChild(node);
        const popperInstance = Popper.createPopper(el, node, {
            placement: 'bottom',
        });
        function show() {
            if (node.hasAttribute('data-show')) {
                node.removeAttribute('data-show');
            } else {
                node.setAttribute('data-show', '');
            }
            popperInstance.update();
        }
        el.addEventListener('click', show);
    }
}
</script>
<div style="font-style: italic;">Success!</div>
"""
    return HTML(js)


def display(doc: Document, height=None):
    """Show annotations on a document.

    Parameters
    ----------
    doc: Document
        The document to show.
    height: str
        The height of the document.

    Returns
    -------
    HTML
        The HTML document.
    """
    doc_id = uuid.uuid4()
    html_doc = (
        f"<div id='{doc_id.hex}' class='doc' style='min-height: {height}'>"
        f'{doc.content}'
        '</div>\n'
    )
    seralizer = AnnotationSerializer(doc.annotations)
    data = json.dumps(seralizer.serialize())
    javascript_code = (
        '<script type="text/javascript">\n'
        f"  annotate('{doc_id.hex}', {data});\n"
        "</script>\n"
    )
    return HTML(html_doc + javascript_code)
