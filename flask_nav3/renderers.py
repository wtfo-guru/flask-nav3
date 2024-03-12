from dominate import tags
from flask import current_app
from visitor import Visitor


class Renderer(Visitor):
    """Base interface for navigation renderers.

    Visiting a node should return a string or an object that converts to a
    string containing HTML.
    """

    def visit_object(self, node):
        """Fallback rendering for objects.

        If the current application is in debug-mode
        (``flask.current_app.debug`` is ``True``), an ``<!-- HTML comment
        -->`` will be rendered, indicating which class is missing a visitation
        function.

        Outside of debug-mode, returns an empty string.
        """
        if current_app.debug:
            return tags.comment(
                "no implementation in {0} to render {1}".format(
                    self.__class__.__name__,
                    node.__class__.__name__,
                ),
            )
        return ""


class SimpleRenderer(Renderer):
    """A very basic HTML5 renderer.

    Renders a navigational structure using ``<nav>`` and ``<ul>`` tags that
    can be styled using modern CSS.

    :param kwargs: Additional attributes to pass on to the root ``<nav>``-tag.
    """

    def __init__(self, **kwargs):
        """Constructor for ``SimpleRenderer``."""
        self.kwargs = kwargs

    def visit_Link(self, node):
        """Returns arefs matching url."""
        return tags.a(node.text, href=node.get_url())

    def visit_Navbar(self, node):
        """Returns navbar classes."""
        kwargs = {"_class": "navbar"}
        kwargs.update(self.kwargs)

        cont = tags.nav(**kwargs)
        ul = cont.add(tags.ul())

        for item in node.items:
            ul.add(tags.li(self.visit(item)))

        return cont

    def visit_View(self, node):
        """Returns arefs."""
        kwargs = {}
        if node.active:
            kwargs["_class"] = "active"
        return tags.a(
            node.text,
            href=node.get_url(),
            title=node.text,
            **kwargs,
        )  # noqa: WPS221

    def visit_Subgroup(self, node):
        """Returns subgroup divs."""
        group = tags.ul(_class="subgroup")
        title = tags.span(node.title)

        if node.active:
            title.attributes["class"] = "active"

        for item in node.items:
            group.add(tags.li(self.visit(item)))

        return tags.div(title, group)

    def visit_Separator(self, node):
        """Returns separator hrs."""
        return tags.hr(_class="separator")

    def visit_Text(self, node):
        """Returns nav-label spans."""
        return tags.span(node.text, _class="nav-label")


class BootStrap5Renderer(Renderer):
    """A very basic Bootstrap 5 renderer.

    Renders a navigational structure using ``<nav>`` and ``<ul>`` tags that
    can be styled using modern CSS.

    :param kwargs: Additional attributes to pass on to the root ``<nav>``-tag.
    """

    def __init__(self, **kwargs):
        """Constructor for ``SimpleRenderer``."""
        self.kwargs = kwargs

    def visit_Link(self, node):
        """Returns arefs matching url."""
        return tags.a(node.text, href=node.get_url(), _class="nav-link")

    def visit_Navbar(self, node):
        """Returns navbar classes."""
        kwargs = self.kwargs.copy()

        addclass = []
        if "class" in self.kwargs:
            addclass = kwargs["class"].split(" ")

        kwargs["class"] = " ".join(addclass + ["navbar", "navbar-expand-lg"])

        cont = tags.nav(**kwargs)
        ul = cont.add(tags.ul(_class=" ".join(addclass + ["nav"])))

        for item in node.items:
            ul.add(tags.li(self.visit(item), _class="nav-item"))

        return cont

    def visit_View(self, node):
        """Returns arefs."""
        kwargs = {"class": "nav-link"}
        if node.active:
            kwargs["_class"] = "nav-link active"
        return tags.a(
            node.text,
            href=node.get_url(),
            title=node.text,
            **kwargs,
        )  # noqa: WPS221

    def visit_Subgroup(self, node):
        """Returns subgroup divs."""
        group = tags.ul(_class="dropdown-menu")
        kwargs = {"data-bs-toggle": "dropdown"}
        title = tags.a(
            node.title,
            href="#",
            _class="nav-link dropdown-toggle",
            **kwargs,
        )

        if node.active:
            title.attributes["class"] = "nav-link dropdown-toggle active"

        for item in node.items:
            group.add(tags.li(self.visit(item), _class="dropdown-item"))

        return tags.div(title, group, _class="dropdown")

    def visit_Separator(self, node):
        """Returns separator hrs."""
        return tags.hr(_class="dropdown-divider")

    def visit_Text(self, node):
        """Returns nav-label spans."""
        return tags.a(node.text, _class="nav-link disabled")
