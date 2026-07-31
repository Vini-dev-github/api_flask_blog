import os
from pathlib import Path

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import click


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"


class Post(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    body: Mapped[str] = mapped_column(sa.String, nullable=False)
    created: Mapped[datetime] = mapped_column(sa.DateTime, default=sa.func.now())
    author: Mapped[int] = mapped_column(sa.ForeignKey("user.id"))

    def __repr__(self) -> str:
        return f"Post(id={self.id!r}, title={self.title!r}, author={self.author!r})"


@click.command("init-db")
def init_db_command():
    global db
    with current_app.app_context():
        db.create_all()
    """Clear the existing data and create new tables."""
    # init_db()
    click.echo("Initialized the database.")


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)
    db_path = Path(app.instance_path) / "blog.sqlite"
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path.resolve().as_posix()}",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    # register the database commands
    app.cli.add_command(init_db_command)
    # initialize the database
    db.init_app(app)

    @app.route("/hello")
    def hello():
        return "Hell-o, world!"

    # register blueprints
    from src.controllers import user, post

    app.register_blueprint(user.app)
    app.register_blueprint(post.app)

    return app
