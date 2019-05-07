function playAudio(src) {
    if (src) {
        const audioPlayer = document.createElement('audio');
        $(audioPlayer).attr('src', src);
        audioPlayer.play();
    }
}

function saveWordsProgress(words) {
    fetch(`${window.location.origin}/update_word_progress/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': Cookies.get('csrftoken')
        },
        body: JSON.stringify({ words })
    }).then(response => console.log(response));
}

async function getUserWords(wordsetId) {
    const response = await fetch(`${window.location.origin}/user_words/${wordsetId}/`);
    const data = await response.json();
    return data.words;
}

function showResults(trainedWords) {
    $('.word-counter').css('visibility', 'hidden');
    $('.progress').css('visibility', 'hidden');

    const source = $('#result-template').html();
    const template = Handlebars.compile(source);
    const html = template(trainedWords);

    $('.card-content').html(html);
    displayResultButtons();
}

function displayResultButtons() {
    const continueTraining = document.createElement('button');
    const backToTrainings  = document.createElement('button');

    const row1 = document.createElement('div');
    const row2 = document.createElement('div');

    $(row1).addClass('row center');
    $(row2).addClass('row center');

    $(continueTraining).addClass('btn waves-effect waves-light red lighten-2');
    $(backToTrainings).addClass('btn waves-effect waves-light red lighten-2');

    $(continueTraining).html('Continue training');
    $(backToTrainings).html('To the list of trainings');

    const cardAction = $('.card-action');

    cardAction.html('');

    $(row1).append(continueTraining);
    $(row2).append(backToTrainings);

    cardAction.append(row1);
    cardAction.append(row2);

    $(continueTraining).click(event => {
        window.location.replace(window.location.href);
    });

    $(backToTrainings).click(event => {
        window.location.replace(`${window.origin}/trainings/`);
    });
}

function updateWordProgress(newWordProgress) {
    const wordProgress = $('.word-progress');
    wordProgress.text(`${newWordProgress}%`);
    $('.tooltipped')[0].dataset.tooltip = `Word progress: ${newWordProgress}%`;
}

function updateProgressBar(current, total) {
    const progressPercent = 100 * current / total;
    $('.determinate').css('width', `${progressPercent}%`);
}

function updateWordNum(current, total) {
    $('.word-num').text(`${current}/${total}`)
}

function initWordProgress(word) {
    const wordProgress = $('.word-progress');
    wordProgress.text(`${word.study_progress}%`);
    $('.tooltipped')[0].dataset.tooltip = `Word progress: ${word.study_progress}%`;
    $('.tooltipped').tooltip();
}

function initDefinition(word) {
    $('.definition').text(word.sense.definitions[0]);
}

function updatePronunciation(word) {
    let phoneticSpelling = '';
    let pronunciationAudio = '';

    if (word.pronunciation) {
        phoneticSpelling = word.pronunciation.phonetic_spelling;
        pronunciationAudio = word.pronunciation.audio;
    }

    $('.pronunciation-spelling').text(`[${phoneticSpelling}]`);
    $('.pronunciation-audio').data('pronunciation-url', pronunciationAudio);
}
