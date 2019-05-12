let amountOfWords = $('.words .card').length;
let successfullyTrainedWords = [];
let unsuccessfullyTrainedWords = [];
let amountOfTableRows = $('#result-table tr').length;

let id;
let cardListened = false;
let spaceClicked = true;
let trainedWords = Array();

const table = document.getElementById('result-table');

function playAudio(src) {
    const audioPlayer = document.createElement('audio');
    $(audioPlayer).attr('src', src);
    audioPlayer.play();
}

function handlePronunciation(event) {
    event.preventDefault();
    playAudio(event.currentTarget.dataset.pronunciationUrl);
    id = Number(event.target.parentElement.parentElement.parentElement.id);
    cardListened = true;
    spaceClicked = false;
}

function toggleVisibility(selector) {
    const element = $(selector);
    if (element.css('visibility') != 'hidden') {
        element.css('visibility', 'hidden');
    } else {
        element.css('visibility', 'visible');
    }
}

function insertRow(bold, className, text) {
    let row = table.insertRow(amountOfTableRows);
    let cell = row.insertCell(0);
    if (bold) {
        cell.style.fontWeight = 'bold';
    }
    cell.className = className;
    cell.innerHTML = text;
    amountOfTableRows++;
}

function updateSuccessfullyTrainedWords(word, isSuccessfullyTrained) {
     fetch(`${window.location.origin}/update_word_progress/`, {
         method: 'POST',
         headers: {
             'Content-Type': 'application/json',
             'X-CSRFToken': Cookies.get('csrftoken')
         },
         body: JSON.stringify({
            'words': [{word, isSuccessfullyTrained}]
         })
     }).then(response => console.log(response));
}

function showResults() {
    const result = $('.results');
    $('.words').replaceWith(result);
    toggleVisibility(result);

    insertRow(true, 'center', 'Successfully trained words');
    successfullyTrainedWords.forEach(function(element) {
        updateSuccessfullyTrainedWords(element, true);
        insertRow(false, 'green-text text-lighten-1', element.toUpperCase());
    });

    insertRow(true, 'center', 'Unsuccessfully trained words');
    unsuccessfullyTrainedWords.forEach(function(element) {
        updateSuccessfullyTrainedWords(element, false);
        insertRow(false, 'red-text text-lighten-2', element.toUpperCase());
    });
}

function toggleState(correct, userText, correctWord) {
    amountOfWords--;

    if (correct) {
        successfullyTrainedWords.push(correctWord);
        toggleVisibility('#' + id + ' > .card-content > .correct');
    }
    else {
        unsuccessfullyTrainedWords.push(correctWord);
        $('#' + id + ' > .card-content > .listen-answer > .incorrect-answer').text(userText);
    }

    toggleVisibility('#' + id + ' > .card-content > .listen-answer');
    toggleVisibility('#' + id + ' > .card-content > .input-field > input');

    $('#' + id + ' > .card-action > .button-no-answer').toggle();
    $('#' + id + ' > .card-action > .button-check').toggle();
    $('#' + id + ' > .card-action > .span-space').toggle();
    $('#' + id + ' > .card-action > .button-next').toggle();

    if (amountOfWords == 0) {
        toggleVisibility('.button-show-results');
    }
}

function updateProgressBar() {
    const progressBar = $('.progress > .determinate');
    let width = Number(progressBar.prop('style')['width'].split('%')[0]);
    width += 100 / $('.words .card').length;
    progressBar.attr('style', 'width: ' + String(width) + '%');
}

function handleCheck() {
    const userText = $('#' + id + ' > .card-content > .input-field > input').val().toLowerCase().trim();
    const correctWord = $('#' + id + ' > .card-content > .listen-answer > .correct-answer').text();
    const correct = userText == correctWord;

    updateProgressBar();
    toggleState(correct, userText, correctWord);
}

function handleNoAnswer() {
    const correctWord = $('#' + id + ' > .card-content > .listen-answer > .correct-answer').text();
    updateProgressBar();
    toggleState(false, '', correctWord);
}

function handleScroll(event) {
    $('html, body').animate({
        scrollTop:
            $(event.target).closest('.card').offset().top + $('.card').outerHeight()
    }, 1000);
}

$(document).ready(() => {
    $('.pronunciation').click((event) => {
        handlePronunciation(event);
    });

    $('.button-no-answer').click((event) => {
        if (!trainedWords.includes(id) && !spaceClicked) {
            handleNoAnswer();
            cardListened = false;
            spaceClicked = true;
            trainedWords.push(id);
        }
    });

    $('.button-check').click((event) => {
        if (!trainedWords.includes(id) && cardListened) {
            handleCheck();
            cardListened = false;
            spaceClicked = true;
            trainedWords.push(id);
        }
    });

    $('.button-next').click(event => {
        handleScroll(event);
    });

    $('.button-show-results').click(event => {
        showResults();
    });

    document.addEventListener('keydown', function (event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            if (!trainedWords.includes(id) && cardListened) {
                handleCheck();
                cardListened = false;
                spaceClicked = true;
                trainedWords.push(id);
            }
            else if (trainedWords.includes(id)) {
                $('#' + id + ' > .card-action > .button-next').click();
            }
        }
        else if (event.keyCode === 32) {
            event.preventDefault();
            if (!trainedWords.includes(id) && !spaceClicked) {
                handleNoAnswer();
                cardListened = false;
                spaceClicked = true;
                trainedWords.push(id);
            }
        }
    });
});
