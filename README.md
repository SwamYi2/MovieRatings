# Ratings50

**This is my final project for CS50 Web development with Python and Javscript**

Ratings50 is a website like [IMDB](https://www.imdb.com/) where you can add ratings and write reviews to movies.

[Watch Demo](https://youtu.be/Lhrq0UkMy6E)

## Distinctiveness and Complexity

Unlike Network and Commerce, Ratings50 works like a public database. Any user can add a movie to this web and other users are allowed to contribute by editing or updating the movie data. In the edit history, any user can see all changes that the movie has had.
Users can also add ratings and write reviews about the movies. Ratings50 will show the average rating score of each movie to everyone who visits the website. For the reviews, the users can upvote or downvote on a review to show if they have the same opinion as the reviewer.

Handling ImageField was a big challenge for me because I haven't used it in the previous projects. As Ratings50 is a database of movies, every movie will have a poster associated with it. Instead of storing multiple images with different aspect ratios, I had to find a way to crop them into the same aspect ratio (the common aspect ratio for movie posters, 2:3). I used python PIL library for editing the images. The save() method of Movie model is also overwritten so that when a new movie is uploaded, the poster will be cropped.
Ratings50 also uses APIs from Tmdb, If the movie the user trying to upload already exists in Tmdb, the user can simply click a button and Ratings50 automatically fill the form with Tmdb data. 
>Note that Tmdb data is only used to fill the form and when the user uploads the movie, that data will be saved in Ratings50's database.


## What's in each file

Ratings50 follows the file structure of the previous Django projects.

- static/ratings50
	- **movie.js** - For the movie page.  Contains javascript functions to fetch APIs to add ratings, get/post reviews and vote reviews. Also resizing the trailer ifame according to the window size.
	- **new_movie.js** - For the new_movie page.  Contains javascript functions to make API calls to Tmdb (through Ratings50) for searching the movie the user trying to upload and getting the data of that movie to fill the form.
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
-   Django
    
    `pip install Django`

Just like previous projects, you can run Ratings50 easily like this:
- First, change the directory to where the manage.py exists
- Then, run this cmd
	`python manage.py runserver`

You can now visit Ratings50 with this url
**http://127.0.0.1:8000/ratings50/**
>Don't forget to add '/ratings50/' after your ip address


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

