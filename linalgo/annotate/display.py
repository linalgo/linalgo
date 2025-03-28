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
        margin-right: 3px;
    }
    .tooltip {
        white-space: pre;
        display: none;
        background: black;
        color: white;
        padding: 4px 8px;
        font-size: 13px;
        border-radius: 4px;
        max-width: 400px;
        text-wrap: wrap;
    }

    .tooltip[data-show] {
        display: block;
    }
    .arrow,
    .arrow::before {
        position: absolute;
        width: 8px;
        height: 8px;
        background: inherit;
    }

    .arrow {
        visibility: hidden;
    }

    .arrow::before {
        visibility: visible;
        content: '';
        transform: rotate(45deg);
    }
    .tooltip[data-popper-placement^='top'] > .arrow {
        bottom: -4px;
    }

    .tooltip[data-popper-placement^='bottom'] > .arrow {
        top: -4px;
    }

    .tooltip[data-popper-placement^='left'] > .arrow {
        right: -4px;
    }

    .tooltip[data-popper-placement^='right'] > .arrow {
        left: -4px;
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
        const elements = document.querySelectorAll(`[id='${annotation.id}']`);
        elements.forEach(el => {
            el.classList.add("underline");
            if (!el.textContent) {
                el.remove()
            }
        });
        const node = document.createElement("div");
        const textnode = document.createTextNode(JSON.stringify(annotation.body, null, 2));
        const arrow = document.createElement("div");
        node.setAttribute("role", "tooltip");
        node.classList.add("tooltip");
        arrow.setAttribute("data-popper-arrow", "");
        arrow.classList.add("arrow");
        doc.appendChild(node);
        node.appendChild(textnode);
        node.appendChild(arrow);
        elements.forEach(el => {
            const popperInstance = Popper.createPopper(el, node, {
                placement: 'bottom',
                modifiers: [
                    {
                        name: 'offset',
                        options: {
                            offset: [0, 8],
                        },
                    },
                ],
            })
            function show() {
                if (node.hasAttribute('data-show')) {
                    node.removeAttribute('data-show');
                } else {
                    node.setAttribute('data-show', '');
                }
                popperInstance.update();
            }
            el.addEventListener('click', show)
        });
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
