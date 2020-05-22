# RESTful API
This repo contains a package with an API to a social network--implemented as a database--with limited functionality

**NOTE** The actual app is not deployed anywhere, so you will need to run it locally!

Do **not** forget to change the SECRET_KEY if you are planning on deploying the app!

The app implements the JWT authentication. All the routes, except for signing up and loggin in, request an authentication token--issued during loggin in.

# API Functionality
## Sign Up
Use `/api/v1/resources/users` to add a new user to the database.

**Request payload:** `username`, `password`, `email`.

**URL example:** `http://localhost:5000/api/v1/resources/users`

## Log In
To log in, use `/api/v1/login`.

**URL example:** `http://localhost:5000/api/v1/login`

## Get all users
Use `/api/v1/resources/users` on your local host.

**Request method:** GET

**URL example:** `http://localhost:5000/api/v1/resources/users`

## Get data about a particular user
Use `/api/v1/resources/users/<string:username>` on your local host.

Specify a user name instead of `<string:username>` in the route.

**Request method:** GET

**URL example:** `http://localhost:5000/api/v1/resources/users/Sarah`

## Create a new post
Use `/api/v1/resources/posts` on your local host.

**Request method:** POST

**Request payload:** `content`

**URL example:** `http://localhost:5000/api/v1/resources/posts`

## Get all posts
Use `/api/v1/resources/posts` on your local host.

**Request method:** GET

**URL example:** `http://localhost:5000/api/v1/resources/posts`

## Get all posts of a current user
Use `/api/v1/resources/posts/myposts` on your local host.

**Request method:** GET

**URL example:** `http://localhost:5000/api/v1/resources/posts/myposts`

## Like a post
Use `/api/v1/resources/likes` on your local host.

**Request method:** POST

**Request params:** `post_id`

**URL example:** `http://localhost:5000/api/v1/resources/likes?post_id=1`

## Unlike a post
Use `/api/v1/resources/likes` on your local host.

**Request method:** DELETE

**Request params:** `post_id`

**URL example:** `http://localhost:5000/api/v1/resources/likes?post_id=1`

## Get all likes
Use `/api/v1/resources/likes` on your local host.

**Request method:** GET

**URL example:** `http://localhost:5000/api/v1/resources/likes`

## Get all likes of a current user
Use `/api/v1/resources/likes/mylikes` on your local host.

**Request method:** GET

**URL example:** `http://localhost:5000/api/v1/resources/likes/mylikes`

## Get analytics--amount of likes by day
Use `/api/v1/analytics/likes` on your local host.

**Request method:** GET

**Request params:** `date_from`, `date_to` (in YYYY-MM-DD format)

**URL example:** `http://localhost:5000/api/v1/analytics/likes?date_from=2020-02-15&date_to=2020-06-23`

## Get analytics--last activity and logging in of a user
Use `/api/v1/analytics/users/<string:username>` on your local host.

**Request method:** GET

Specify a user name instead of `<string:username>` in the route.

**URL example:** `http://localhost:5000/api/v1/analytics/users/John`
