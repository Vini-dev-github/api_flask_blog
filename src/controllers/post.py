from flask import Blueprint, request
from src.app import Post, db
from http import HTTPStatus

app = Blueprint("post", __name__, url_prefix="/posts")


def _create_post():
    data = request.get_json()
    post = Post(title=data["title"], body=data["body"], author=data["author"])
    db.session.add(post)
    db.session.commit()


@app.route("/", methods=["GET", "POST"])
def handle_posts():
    if request.method == "POST":
        _create_post()
        return {"message": "Post created successfully"}, HTTPStatus.CREATED

    posts = Post.query.all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "body": p.body,
            "author": p.author,
            "created": p.created.isoformat() if p.created else None,
        }
        for p in posts
    ]
