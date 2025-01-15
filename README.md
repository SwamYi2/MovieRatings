# Movie Ratings

**This project is initially developed as my final project for a web development course**

Ratings is a website like [IMDB](https://www.imdb.com/) where you can add ratings and write reviews to movies.

[You can watch the demo here](https://youtu.be/Lhrq0UkMy6E)

I also added a feature where you can use TMDB Api to get data for a new movie you want to add to this website.
** Warning: You will need to add your own TMDB Api key in views.py for this feature. But it's not a requirement for running this app **

Movie Ratings follows the file structure of the previous Django projects.

- static/ratings50
  - **movie.js** - For the movie page. Contains javascript functions to fetch APIs to add ratings, get/post reviews and vote reviews. Also resizing the trailer ifame according to the window size.
  - **new_movie.js** - For the new_movie page. Contains javascript functions to make API calls to Tmdb (through Ratings50) for searching the movie the user trying to upload and getting the data of that movie to fill the form.
  - **style.scss** - Contains style sheet for all pages
- templates/ratings50
  - **login.html** - Login page
  - **register.html** - Register page
  - **layout.html** - base template for all other HTML files
  - **index.html** - Index page that shows all movies
  - **movie.html** - A page that shows all details about a movie, including reviews
  - **editlog.html** - A page that shows all changes that a movie has had
  - **new_movie.html** - To add a new movie
  - **search.html** - To find a movie and filter the results by choosing genres
- ratings50/
  - **models.py** - Contains Movie. Genre. Certification. Rating. Review and Vote and EditLog models.
  - **admin.py** - Registered models to edit in Admin page.
  - **url.py** - Contains all Urls
  - **views.py** - Functions to handle all requests, add data to the database and return data to the user
- media/posters - the path where the posters of the movies are stored.

## How to run

### If you haven't installed django:

- Django

  `pip install Django`

** Also, don't forget to install packages from requirements.txt **

Just like previous projects, you can run Ratings50 easily like this:

- First, change the directory to where the manage.py exists
- Then, run this cmd
  `python manage.py runserver`

You can now visit Ratings50 with this url
**http://127.0.0.1:8000/ratings50/**

> Don't forget to add '/ratings50/' after your ip address

## Usage

### Add a movie

After creating an account, you should see the **Add Movie** link inside the nav-bar. Clicking it will take you to a form where you can upload a movie item.

**Don't know all the details about your movie?**
No worries, if your movie already exists on Tmdb, you can search it in the small form under the main one. And when you find it, Ratings50 will fill the form for you.

### Edit a movie

When visiting a movie page, you should see two links at the bottom-right of the page. The first link will take you to the edit form if you're logged in. The last one will take you to a page which shows all the changes that has been made to the movie.

### Rating

You can rate a movie by clicking the rate button on the right side of the poster. In mobile, it's under the poster

### Review

You can write a review to a movie by clicking 'Write a review' button. You are required to add rating before posting a review. You can also vote reviews by clicking up and down arrows on left side of the reviews.

### Search

Ratings50 has 2 places to search. The first one is at the end of the nav-bar where you can search movies by title. If you want to filter the results by genres, use the 'Search' link on the nav-bar.
