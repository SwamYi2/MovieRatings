// Genres are multiselect field but made to look like check boxes 
// if we come from edit route, genres are already checked
// give checked appearance to checked inputs 
let genres = document.querySelector(".genre-boxes");
genres.querySelectorAll('.genre').forEach(div => {
    if (div.querySelector('input').checked) {
        div.className = 'genre checked';
    } else {
        div.className = 'genre';
    }
})

// if user clicks genre boxes, check the box's input and change it's appearence
genres.querySelectorAll('.genre').forEach(div => {
    div.addEventListener('click', () => {
        if (div.querySelector('input').checked) {
            div.querySelector('input').checked = false;
            div.className = 'genre';
        } else {
            div.querySelector('input').checked = true;
            div.className = 'genre checked';
        }
    })
})

// FOR TMDB SEARCH
// Copy the main form's title and date fields to the tmdb form
document.querySelector("#id_title").addEventListener('keyup', () => {
    document.querySelector("#tmdb-title").value = document.querySelector("#id_title").value;
})

document.querySelector("#id_release_date").addEventListener('change', () => {
    date = document.querySelector("#id_release_date").value.substring(0,4);
    document.querySelector("#tmdb-year").value = date;
})

// API for tmdb search
document.querySelector("#tmdb-search").addEventListener('click', () => {
    document.querySelector("#tmdb-results").innerHTML = "";
    fetch('tmdb_search', {
        method: 'POST',
        body: JSON.stringify({
            query: document.querySelector("#tmdb-title").value,
            year: document.querySelector("#tmdb-year").value
      })
    }).then(response => response.json())
    .then(data => {
        // insert results to the tmdv-results div
        data.results.results.forEach(movie => insert_result(movie, document.querySelector("#tmdb-results")))
    })
    return false
})

function insert_result(movie, parent)
{
    var temp = document.querySelector("template");
    var clon = temp.content.cloneNode(true);

    clon.querySelector("#poster").src = `https://image.tmdb.org/t/p/w92/${movie.poster_path}`
    clon.querySelector("#title").innerHTML = movie.title;
    clon.querySelector("#release-date").innerHTML = movie.release_date;
    clon.querySelector("#id-button").dataset.id = movie.id;
    clon.querySelector("#data-button").dataset.id = movie.id;

    parent.append(clon)
}

function fill_id(data) {
    document.querySelector("#id_tmdb_id").value = data.getAttribute("data-id");
    document.querySelector("#id_tmdb_id").focus()
}

//API for using data from Tmdb
function fill_data(data) {
    var id = data.getAttribute("data-id");

    fetch('tmdb_data', {
        method: 'POST',
        body: JSON.stringify({
            id: data.getAttribute("data-id")
      })
    }).then(response => response.json())
    .then(data => {
        document.querySelector("#id_title").value = data.data.title;
        document.querySelector("#id_overview").value = data.data.overview;

        var poster_url = `https://image.tmdb.org/t/p/w500/${data.data.poster_path}`
        loadURLToInputFiled(poster_url) 

        var genre_boxes = document.querySelectorAll('.genre')
        genre_boxes.forEach(genre_box => {
            genre_box.querySelector('input').checked = false;
            genre_box.style.backgroundColor = '#31373f';
        })

        data.data.genres.forEach(genre => {
            genre_boxes.forEach(genre_box => {
                if (genre_box.innerHTML.includes(genre.name)) {
                    genre_box.querySelector('input').checked = true;
                    genre_box.style.backgroundColor = 'grey';
                }
            })
        })

        var certification = document.querySelector("#id_certification");
        var US_release_date = data.data.release_dates.results.filter(result => result.iso_3166_1 === 'US');
        var tmdb_certification = US_release_date[0].release_dates[0].certification;

        certification.querySelectorAll('option').forEach(option => {
            if (option.innerHTML === tmdb_certification) {
                certification.value = option.value;
            }
        })

        document.querySelector("#id_release_date").value = data.data.release_date;
        document.querySelector("#id_tmdb_id").value = data.data.id;

        var director = data.data.credits.crew.find(person => person.job === "Director")
        console.log(director)
        document.querySelector("#id_director").value = director.name;

        var trailer_url = data.data.videos.results.find(video => video.type ===  "Trailer" && video.site === "YouTube")
        document.querySelector("#id_trailer_url").value = `https://www.youtube.com/embed/${trailer_url.key}`

        document.querySelector("#id_title").focus()

    })
}

//https://stackoverflow.com/a/70485949
function loadURLToInputFiled(url){
    getImgURL(url, (imgBlob)=>{
      // Load img blob to input
      // WIP: UTF8 character error
      let fileName = 'poster.jpg'
      let file = new File([imgBlob], fileName,{type:"image/jpeg", lastModified:new Date().getTime()}, 'utf-8');
      let container = new DataTransfer(); 
      container.items.add(file);
      document.querySelector("#id_poster").files = container.files;
      
    })
  }
  // xmlHTTP return blob respond
  function getImgURL(url, callback){
    var xhr = new XMLHttpRequest();
    xhr.onload = function() {
        callback(xhr.response);
    };
    xhr.open('GET', url);
    xhr.responseType = 'blob';
    xhr.send();
  }