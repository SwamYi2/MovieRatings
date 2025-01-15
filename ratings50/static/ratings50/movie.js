var rate_modal = document.querySelector('#rate-modal');
var modal_stars = rate_modal.querySelector('.stars');
var stars = modal_stars.querySelectorAll('span');
var submitted_score = rate_modal.querySelector('#score').value;
var movie_id = document.querySelector('.movie-container').dataset.movie_id;

var review_modal = document.querySelector('#review-modal')
var rating_info = review_modal.querySelector('.rating-info')

// Check the stars according to user's submitted score
for (let i = 0; i < submitted_score; i++) {
    stars[i].className = "fa-solid fa-star checked"
}

// When the mouse leave the stars return checked values to normal
modal_stars.addEventListener('mouseleave', () => {
    var submitted_score = rate_modal.querySelector('#score').value;
    stars.forEach(star => {
        star.className = "fa-solid fa-star"
    })

    for (let i = 0; i < submitted_score; i++) {
        stars[i].className = "fa-solid fa-star checked"
    }

})

// check the star that the mouse hovers upon
modal_stars.querySelectorAll('span').forEach(star => {
    star.addEventListener('mouseenter', () => {
        var value = star.dataset.value;
        stars.forEach(star => {
            star.className = "fa-solid fa-star"
        })

        for (let i = 0; i < value; i++) {
            stars[i].className = "fa-solid fa-star checked"
        }
    })

    // When the user click a star, change the submit score value
    star.addEventListener('click', () => {
        var value = star.dataset.value;
        rate_modal.querySelector('#score').value = value;
    })
});

// Post a rating
rate_modal.querySelector('#rate-btn').addEventListener('click', () => {
    axios.post('rate', {
        movie_id: movie_id,
        score: rate_modal.querySelector("#score").value
    })
    .then(function (response) {
        // Add the changed data to the Html
        data = response.data

        rate_modal.querySelector("#error").style.display ="none";

        document.querySelector('#rating-score').innerHTML = 
        `<span class="fa-solid fa-star checked"></span>${data.avg_rating}`;

        document.querySelector('#user-rating').innerHTML =
        `<span class="fa-solid fa-star checked"></span>Your rating: ${data.user_rating}`;

        // for the review modal
        rating_info.innerHTML = `<p>Your Rating:  <span class="fa-solid fa-star checked"></span>
            ${data.user_rating}/10</p>`

        // Allow user to post review
        review_modal.querySelector('#review-btn').disabled = false;

        let modal = bootstrap.Modal.getInstance(rate_modal)
        modal.hide()
    })
    .catch(function (err) {
        // Add the error message
        var error = rate_modal.querySelector("#error");

        error.style.display = "block"
        error.innerHTML = err.response.data.Error;
    });
})

// Post a review
review_modal.querySelector('#review-btn').addEventListener('click', () => {
    var headline = review_modal.querySelector('#headline').value;
    var review = review_modal.querySelector('#review').value;

    axios.post(`reviews/${movie_id}`, {
        movie_id: movie_id,
        headline: headline,
        review: review
    })
    .then(function (response) {
        // In case we're showing an error, hide it
        review_modal.querySelector("#error").style.display = "none";

        let modal = bootstrap.Modal.getInstance(review_modal)
        modal.hide()
        // Refresh the reviews
        get_reviews();
    })
    .catch(function (err) {
        // Add the error message
        var error = review_modal.querySelector("#error");
        error.style.display = "block";
        error.innerHTML = err.response.data.Error;
    });
})

function get_reviews() {

    fetch(`reviews/${movie_id}`)
    .then(response => response.json())
    .then(data => {
        if (data.reviews.length === 0) {
            document.querySelector("#reviews").innerHTML = "No reviews";
        } else {
            document.querySelector("#reviews").innerHTML = "<h4>Reviews</h4>";
            data.reviews.forEach(review => insert_review(review, document.querySelector("#reviews")))
        }
    })
}

// Add the reviews to the parent div
function insert_review(review, parent)
{
    var temp = document.querySelector("template");
    var clon = temp.content.cloneNode(true);

    clon.querySelector(".username").innerHTML = `<b>${review.username}</b>`;
    clon.querySelector(".headline").innerHTML = review.headline;
    clon.querySelector(".review").innerHTML = review.text;
    clon.querySelector(".rating").innerHTML = `<span class="fa-solid fa-star checked"></span>${review.rating_score}/10`;
    clon.querySelector(".datetime").innerHTML = review.date;
    var vote_count = clon.querySelector("#vote-count");
    vote_count.innerHTML = review.votes;

    var up_arrow = clon.querySelector("#up-arrow");
    var down_arrow = clon.querySelector("#down-arrow");
    // Add EventListeners to the voting arrows
    up_arrow.onclick = () => vote_review(up_arrow, down_arrow, vote_count, review.id, true)
    down_arrow.onclick = () => vote_review(up_arrow, down_arrow, vote_count, review.id, false)

    // Change the class of arrows if the user has already voted
    if (review.up_voted) {
        up_arrow.className = "fa-solid fa-caret-up fa-xl checked";
    }
    if (review.down_voted) {
        down_arrow.className = "fa-solid fa-caret-down fa-xl checked";
    }

    // Show a delete button if the user can delete this review
    if (review.deleteable) {
        delete_btn = clon.querySelector("#delete-btn")
        confirm_message = clon.querySelector("#confirm")
        delete_btn.disabled = false
        delete_btn.onclick = () => {
            if (confirm_message.style.display === "none") {
                confirm_message.style.display = "inline-block";
                delete_btn.innerHTML = "Yes";
            } else {
                delete_review(review.id);
            }
        }
    } else {
        clon.querySelector('.delete').innerHTML = "";
    }

    parent.append(clon)
}

function vote_review(up_arrow, down_arrow, vote_count, review_id, up) {
    axios.post('vote_review', {
        review_id: review_id,
        up: up
    })
    .then(function (response) {
        data = response.data

        document.querySelector("#review-error").style.display = "none";

        // reset the class of arrows to default
        up_arrow.className = "fa-solid fa-caret-up fa-xl";
        down_arrow.className = "fa-solid fa-caret-down fa-xl"

        // Change the class according to returned data
        if (data.up_voted) {
            up_arrow.className = "fa-solid fa-caret-up fa-xl checked";
        }
        if (data.down_voted) {
            down_arrow.className = "fa-solid fa-caret-down fa-xl checked";
        }
        vote_count.innerHTML = data.vote_count;
    })
    .catch(function (err) {
        // Add the error message
        var error = document.querySelector("#review-error");

        error.style.display = "block"
        error.innerHTML = err.response.data.Error;
        error.focus()
    });
}

function delete_review(review_id) {
    axios.put(`reviews/${movie_id}`, {
        review_id: review_id,
        action: 'delete'
    })
    .then(function (response) {
        document.querySelector("#review-error").style.display = "none";
        get_reviews();
    })
    .catch(function (err) {
        var error = document.querySelector("#review-error");

        error.style.display = "block"
        error.innerHTML = err.response.data.Error;
        error.focus()
    });
}

// Change the iframe height when user resize the window
var iframe = document.querySelector('iframe');
if (iframe != null && iframe != undefined) {
    window.addEventListener('resize', () => {
        resize_iframe();
      });
    
      resize_iframe();
}
function resize_iframe() {
    var device_width = (window.innerWidth > 0) ? window.innerWidth : screen.width;
    if (device_width < 992) {
        var iframe_height = (9 * device_width) / 16;
    } else {
        var iframe_height = (9 * (device_width / 2)) / 16;
    }

    iframe.height = iframe_height;
}

get_reviews();
