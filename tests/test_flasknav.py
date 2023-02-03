import pytest
from flask import Flask

from flask_nav3.elements import View


@pytest.fixture()
def app():
    """App fixture."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "testing.local"

    @app.route("/hello/<arg1>/")
    def hello(arg1):  # noqa: WPS430
        return str(app.hello_view.active)  # type: ignore [attr-defined]

    return app


@pytest.fixture()
def hello_view(app):
    """Hello view fixture."""
    vv = View("notext", "hello", arg1=1, q1="q")
    app.hello_view = vv
    return vv


def test_view_arguments(app, hello_view):
    """Test view argumeents."""
    with app.app_context():

        # since we're using the app context, flask should generate an
        # external url. inside a real request, chances are a relative url
        # would be generated instead
        assert hello_view.get_url() == "http://testing.local/hello/1/?q1=q"


def test_active_without_query(app, hello_view):
    """Test active without query."""
    with app.app_context():
        url = "{0}&foo=bar".format(hello_view.get_url())

    with app.test_client() as cc:
        assert cc.get(url).data.decode("utf8") == "True"


def test_active_with_query(app, hello_view):
    """Test active with query."""
    hello_view.ignore_query = False

    with app.app_context():
        url = "{0}&foo=bar".format(hello_view.get_url())

    with app.test_client() as cc:
        assert cc.get(url).data.decode("utf8") == "False"
