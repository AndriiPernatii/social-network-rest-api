from flask import request, jsonify, make_response
from api import app, db, bcrypt
from api.models import User, Post, Like
from datetime import datetime, timedelta
import jwt
from functools import wraps

#FUNCTIONALITY DECORATORS

def jwt_required(foo):
    """
    Validates an access token each time a user makes requests to
    correspondingly decorated routes.
    """
    @wraps(foo)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        if not token:
            return make_response("Token is missing", 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(username=data["username"]).first()
        except:
            return make_response("Token is invalid", 401)
        return foo(current_user, *args, **kwargs)
    return decorated

def update_activity(foo):
    """
    Updates User.last_activity every time a user makes requests to
    correspondingly decorated routes.
    """
    @wraps(foo)
    def decorated(current_user, *args, **kwargs):
            user = User.query.filter_by(id=current_user.id).first()
            user.last_activity = datetime.utcnow()
            db.session.commit()
            return foo(current_user, *args, **kwargs)
    return decorated

def update_login(foo):
    """
    Updates User.last_seen every time a user makes requests to the login route.
    """
    @wraps(foo)
    def decorated(current_user, *args, **kwargs):
            user = User.query.filter_by(id=current_user.id).first()
            user.last_seen = datetime.utcnow()
            db.session.commit()
            return foo(current_user, *args, **kwargs)
    return decorated

#SIGNUP AND LOGIN ROUTES

@app.route("/api/v1/resources/users", methods=["POST"])
def signup():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(username=data["username"], email=data["email"],
                    password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"Message" : "A new user has been created!"})

@app.route("/api/v1/login")
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response("Could not verify", 401)
    user = User.query.filter_by(username=auth.username).first()
    if user and bcrypt.check_password_hash(user.password, auth.password):
        token = jwt.encode({"username" : user.username,
                            "exp" : datetime.utcnow()+timedelta(minutes=120)},
                            key=app.config['SECRET_KEY'])
        user.last_seen = datetime.utcnow()
        db.session.commit()
        return jsonify({"token" : token.decode("UTF-8")})
    return make_response("Could not verify", 401)

#USER RESOURCE FUNCTIONALITY
@app.route("/api/v1/resources/users", methods=["GET"])
@jwt_required
@update_activity
def get_all_users(current_user):
    users = User.query.all()
    result = []
    for user in users:
        username = user.username
        result.append(username)
    return jsonify({"Users" : result})

@app.route("/api/v1/resources/users/<string:username>", methods=["GET"])
@jwt_required
@update_activity
def get_one_user(current_user, username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"Message" : "No user found"})
    user_data = {}
    user_data["email"] = user.email
    user_data["last logged in"] = user.last_seen
    user_data["last activity"] = user.last_activity
    user_data["number of posts"] = len(user.posts)
    return jsonify({user.username : user_data})

#POST RESOURCE FUNCTIONALITY

@app.route("/api/v1/resources/posts", methods=["POST"])
@jwt_required
@update_activity
def create_post(current_user):
    data = request.get_json()
    new_post = Post(content=data["content"], user_id=current_user.id)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"Message": "A new post has been created."})

@app.route("/api/v1/resources/posts", methods=["GET"])
@jwt_required
@update_activity
def get_all_posts(current_user):
    posts = Post.query.all()
    result = []
    for post in posts:
        post_data = {}
        post_data["content"] = post.content
        post_data["author"] = post.author.username
        post_data["posted on"] = post.creation_date
        result.append(post_data)
    return jsonify({"Posts" : result})

@app.route("/api/v1/resources/posts/myposts", methods=["GET"])
@jwt_required
@update_activity
def get_all_posts_of_user(current_user):
    posts = Post.query.filter_by(user_id=current_user.id).all()

    if not posts:
        return jsonify({"Message": "There are no posts in your account"})

    result = []
    for post in posts:
        post_data = {}
        post_data["content"] = post.content
        post_data["posted on"] = post.creation_date
        result.append(post_data)
    return jsonify({"User: " : current_user.username, "Posts: " : result})

#LIKE RESOURCE FUNCTIONALITY

@app.route("/api/v1/resources/likes", methods=["POST"])
@jwt_required
@update_activity
def put_like(current_user):
    post_id = request.args.get("post_id")
    like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if like:
        return jsonify({"Message": "You have already likes this post."})
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        return jsonify({"Message": "There are no such post"})

    new_like = Like(user_id=current_user.id, post_id=post_id)
    db.session.add(new_like)
    db.session.commit()
    return jsonify({"Message: " : f"You have put a like to post {post_id}"})

@app.route("/api/v1/resources/likes", methods=["DELETE"])
@jwt_required
@update_activity
def unlike(current_user):
    post_id = request.args.get("post_id")
    like = Like.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if not like:
        return jsonify({"Message": "This post has no likes by you"})
    db.session.delete(like)
    db.session.commit()
    return jsonify({"Message": "You have unliked this post :( "})

@app.route("/api/v1/resources/likes", methods=["GET"])
@jwt_required
@update_activity
def get_all_likes(current_user):
    likes = Like.query.all()
    if not likes:
        return jsonify({"Message": "There are no likes so far."})
    result = []
    for like in likes:
        like_data = {}
        like_data["Post"] = like.likedpost.content
        like_data["Put on"] = like.date_put
        like_data["Liked by"] = like.likedby.username
        result.append(like_data)
    return jsonify({"Likes: " : result})

@app.route("/api/v1/resources/likes/mylikes", methods=["GET"])
@jwt_required
@update_activity
def get_all_likes_by_user(current_user):
    likes = Like.query.filter_by(user_id=current_user.id).all()
    if not likes:
        return jsonify({"Message": "You have not put any likes so far."})
    result = []
    for like in likes:
        like_data = {}
        like_data["Post"] = like.likedpost.content
        like_data["Put on"] = like.date_put
        result.append(like_data)
    return jsonify({"User: " : current_user.username, "Likes: " : result})

#ANALYTICS FUNCTIONALITY

@app.route("/api/v1/analytics/likes", methods=["GET"])
@jwt_required
@update_activity
def likes_by_day(current_user):
    datetime_from = datetime.strptime(request.args.get("date_from"), "%Y-%m-%d")
    datetime_to = datetime.strptime(request.args.get("date_to"), "%Y-%m-%d")
    likes = db.session.query(db.func.count(Like.id),
        Like.date_put).filter(Like.date_put<=datetime_to
        +timedelta(days=1)).filter(Like.date_put>=datetime_from).group_by(
        db.func.date(Like.date_put)).all()
    likes_data = []
    for i in range(len(likes)):
        like_data={}
        like_data["count of likes"] = likes[i][0]
        like_data["day"] = likes[i][1].replace(hour=0, minute=0, second=0,
                                               microsecond=0)
        likes_data.append(like_data)
    return jsonify({"likes":likes_data})

@app.route("/api/v1/analytics/users/<string:username>")
@jwt_required
def get_user_activity(current_user, username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"Message": "There is not such user."})
    activity_data = {}
    activity_data["last logged in"] = user.last_seen
    activity_data["last activity"] = user.last_activity
    return jsonify({f"User {user.username}" : activity_data})
