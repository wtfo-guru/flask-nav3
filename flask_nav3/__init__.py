import re
import sys
from importlib import import_module

if sys.version_info >= (3, 7):
    from collections.abc import MutableMapping
else:
    from collections import MutableMapping


def register_renderer(app, iid, renderer, force=True):
    """Registers a renderer on the application.

    :param app: The :class:`~flask.Flask` application to register the renderer
                on
    :param iid: Internal id-string for the renderer
    :param renderer: Renderer to register
    :param force: Whether or not to overwrite the renderer if a different one
                  is already registered for ``iid``
    """
    renderers = app.extensions.setdefault("nav_renderers", {})

    if force:
        renderers[iid] = renderer
    else:
        renderers.setdefault(iid, renderer)


def get_renderer(app, iid):  # noqa: WPS210
    """Retrieve a renderer.

    :param app: :class:`~flask.Flask` application to look ``iid`` up on
    :param iid: Internal renderer id-string to look up
    """
    renderer = app.extensions.get("nav_renderers", {})[iid]

    if isinstance(renderer, tuple):
        mod_name, cls_name = renderer
        mod = import_module(mod_name)

        clsnm = mod
        for name in cls_name.split("."):
            clsnm = getattr(clsnm, name)

        return clsnm

    return renderer


class NavbarRenderingError(Exception):
    """The NavbarRenderingError class."""


class ElementRegistry(MutableMapping):  # type: ignore [type-arg]
    """The ElementRegistry class."""

    def __init__(self):
        """Constructor for ElementRegistry."""
        self._elems = {}

    def __getitem__(self, key):
        """Returns key item from elements."""
        the_item = self._elems[key]

        if callable(the_item):
            try:
                return the_item()
            except Exception as ee:
                # we wrap the exception, because otherwise things get
                # confusing if __getitem__ returns a KeyError

                # fixme: could use raise_from here on Py3
                raise NavbarRenderingError(
                    "Encountered {0} while trying to render navbar".format(repr(ee)),
                )

        return the_item

    def __setitem__(self, key, ivalue):
        """Sets key => ivalue in elements."""
        self._elems[key] = ivalue

    def __delitem__(self, key):  # noqa: WPS603
        """Delete key item from elements."""
        self._elems.pop(key)

    def __iter__(self):
        """__iter__ magic function."""
        # TODO: Determine if the WPS328 is relavent
        for key in self._elems.keys():  # noqa: WPS328
            return self[key]

    def __len__(self):
        """Returns the number of elements."""
        return len(self._elems)


class Nav(object):
    """The Flask-Nav extension.

    :param app: An optional :class:`~flask.Flask` app to initialize.
    """

    def __init__(self, app=None):
        """Construct a Nav instance.

        Parameters
        ----------
        app : Flask, optional
            The Flask app, by default None
        """
        self.elems = ElementRegistry()

        # per default, register the simple renderer
        simple = "{0}.renderers".format(__name__), "SimpleRenderer"
        bootstrap5 = "{0}.renderers".format(__name__), "BootStrap5Renderer"
        self._renderers = [
            ("simple", simple),
            ("bootstrap5", bootstrap5),
            (None, simple, False),
        ]

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize an application.

        :param app: A :class:`~flask.Flask` app.
        """
        if not hasattr(app, "extensions"):
            app.extensions = {}

        app.extensions["nav"] = self
        app.add_template_global(self.elems, "nav")

        # register some renderers
        for args in self._renderers:
            register_renderer(app, *args)

    def navigation(self, iid=None):
        """Function decorator for navbar registration.

        Convenience function, calls :meth:`.register_element` with ``iid`` and
        the decorated function as ``elem``.

        :param iid: ID to pass on. If ``None``, uses the decorated functions
                   name.
        """

        def wrapper(ff):
            self.register_element(iid or ff.__name__, ff)
            return ff

        return wrapper

    def register_element(self, iid, elem):
        """Register navigational element.

        Registers the given navigational element, making it available using the
        id ``iid``.

        This means that inside any template, the registered element will be
        available as ``nav.`` *id*.

        If ``elem`` is callable, any attempt to retrieve it inside the template
        will instead result in ``elem`` being called and the result being
        returned.

        :param iid: Id to register element with
        :param elem: Element to register
        """
        self.elems[iid] = elem

    def renderer(self, iid=None, force=True):
        """Class decorator for Renderers.

        The decorated class will be added to the list of renderers kept by this
        instance that will be registered on the app upon app initialization.

        :param iid: Id for the renderer, defaults to the class name in snake
                   case.
        :param force: Whether or not to overwrite existing renderers.
        """

        def _(cls):
            name = cls.__name__
            sn = name[0] + re.sub("([A-Z])", r"_\1", name[1:])

            self._renderers.append((iid or sn.lower(), cls, force))
            return cls

        return _
