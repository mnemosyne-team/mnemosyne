let words = [];
let trainedWords = {successfullyTrainedWords: [], unsuccessfullyTrainedWords: []};
let currentWordIndex = 0;
const MAX_TYPOS = 3;
let currentTypoCount = 0;


$(document).ready(() => {

  $('.pronunciation-audio').click(event => {
      playAudio($('.pronunciation-audio').data('pronunciation-url'));
  });

  function playAudio(src) {
    const audioPlayer = document.createElement('audio');
    $(audioPlayer).attr('src', src);
    audioPlayer.play();
  }

  function createCharInput(index) {
    const charInput = document.createElement('input');
    $(charInput).addClass('char-input center');
    $(charInput).attr('id', `char-${index}`);
    $(charInput).attr('type', 'text');
    $(charInput).attr('maxlength', '1');
    $(charInput).attr('readonly', true);
    $(charInput).css('width', '20px');
    $(charInput).css('margin-left', '10px');
    $(charInput).data('char-pos', index);
    return charInput;
  }

  function createWordInput(wordLength) {
    for (let i=0; i < wordLength; i++) {
      $('.input').append(createCharInput(i));
    }
  }

  function saveWordProgress(word, isSuccessfullyTrained) {
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

  $('#show-answer').click(event => {
    const word = words[currentWordIndex].word.toUpperCase();
    $($('.char-input')[0]).attr('readonly', true);
    for (let letterIndex in word) {
      const charInput = $(`input#char-${letterIndex}`);
      charInput.val(word[letterIndex]);
      charInput.addClass('valid');
    }
    currentTypoCount = MAX_TYPOS;
    saveWordProgress(word, false);
    updateWordProgress(words[currentWordIndex]);
    togglePronunciation();
    toggleButtons();
    playAudio($('.pronunciation-audio').data('pronunciation-url'));
    trainedWords.unsuccessfullyTrainedWords.push(word)
  });

  document.addEventListener('keydown', function (event) {
    if (event.keyCode === 13) {
        const showAnswer = $('#show-answer');
        if (showAnswer.css('display') === 'inline-block') {
          showAnswer.trigger('click');
          return;
        } else {
          $('#next').trigger('click');
          return;
        }
    }

    const word = words[currentWordIndex].word.toUpperCase();

    for (let charInput of $('.char-input')) {
      const charInputObj = $(charInput);

      if (charInputObj.val().length > 0) {
        continue;
      }

      if (charInputObj.val().length === 0) {
        const charPos = Number(charInputObj.data('char-pos'));
        if (String.fromCharCode(event.keyCode) === word[charPos]) {
          charInputObj.val(String.fromCharCode(event.keyCode));
          charInputObj.addClass('valid');
          charInputObj.attr('readonly', true);
          $(`#char-${charPos + 1}`).attr('readonly', false);
          if (Number(charInputObj.data('char-pos')) === word.length - 1) {
            togglePronunciation();
            playAudio($('.pronunciation-audio').data('pronunciation-url'));
            toggleButtons();
            updateWordProgress(words[currentWordIndex]);
            const isSuccessfullyTrained = currentTypoCount < MAX_TYPOS;
            saveWordProgress(word, isSuccessfullyTrained);
            if (isSuccessfullyTrained) {
              trainedWords.successfullyTrainedWords.push(word);
            } else {
              trainedWords.unsuccessfullyTrainedWords.push(word);
            }
          }
        } else {
          currentTypoCount++;
          charInputObj.addClass('invalid');
          setTimeout(function () {
            charInputObj.removeClass('invalid');
          }, 500);
        }
        break;
      }
    }
  });

  $('#next').click(event => {
    if (currentWordIndex < words.length - 1) {
      currentWordIndex++;
      const currentWord = words[currentWordIndex];
      toggleButtons();
      togglePronunciation();
      updateCard(currentWord);
      currentTypoCount = 0;
    } else if (currentWordIndex === words.length - 1) {
      showResults();
    }
  });

  function showResults() {
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

    $(continueTraining).addClass('btn waves-effect waves-light red lighten-2');
    $(backToTrainings).addClass('btn waves-effect waves-light red lighten-2');

    $(continueTraining).html('Continue training');
    $(backToTrainings).html('To the list of trainings');

    $(continueTraining).css('margin-bottom', '20px');

    $('.card-action').html('');

    $('.card-action').append(continueTraining);
    $('.card-action').append(backToTrainings);

    $(continueTraining).click(event => {
      window.location.replace(window.location.href);
    });

    $(backToTrainings).click(event => {
      window.location.replace(`${window.origin}/trainings/`);
    });
  }

  function updateWordProgress(word) {
      const wordProgress = $('.word-progress');
      if (word.study_progress < 100 && currentTypoCount < MAX_TYPOS) {
        wordProgress.text(`${word.study_progress + 25}%`);
      } else if (word.study_progress > 0 && currentTypoCount >= MAX_TYPOS) {
        wordProgress.text(`${word.study_progress - 25}%`);
      }
      $('.tooltipped')[0].dataset.tooltip = `Word progress: ${wordProgress.text()}`;
  }

  function togglePronunciation() {
    const pronunciation = $('.pronunciation');
    if (pronunciation.css('visibility') === 'visible') {
      pronunciation.css('visibility', 'hidden');
    } else {
      pronunciation.css('visibility', 'visible');
    }
  }

  function toggleButtons() {
    $('#next').toggle();
    $('#show-answer').toggle();
  }

  function updateCard(word) {
    $('.input').html('');
    createWordInput(word.word.length);
    updatePronunciation(word);
    initDefinition(word);
    initWordProgress(word);
    updateProgressBar(currentWordIndex);
    updateWordNum();
    $($('.char-input')[0]).attr('readonly', false);
  }

  function updatePronunciation(word) {
    $('.pronunciation-spelling').text(`[${word.pronunciation.phonetic_spelling}]`);
    $('.pronunciation-audio').data('pronunciation-url', word.pronunciation.audio);
  }

  function initDefinition(word) {
    $('.definition').text(word.sense.definitions[0]);
  }

  function initWordProgress(word) {
    const wordProgress = $('.word-progress');
    wordProgress.text(`${word.study_progress}%`);
    $('.tooltipped')[0].dataset.tooltip = `Word progress: ${word.study_progress}%`;
    $('.tooltipped').tooltip();
  }

  function updateProgressBar() {
    const progressPercent = 100 * (currentWordIndex+1) / words.length;
    $('.determinate').css('width', `${progressPercent}%`);
  }

  function updateWordNum() {
      $('.word-num').text(`${currentWordIndex+1}/${words.length}`)
  }

  let category = $('input[name="category"]').val();
  fetch(`${window.location.origin}/user_words/${category}/`)
      .then(response => response.json())
      .then(data => {
        words = data.words;
        updateCard(words[currentWordIndex]);
        $('.char-input').on('input', function() {
          const charPos = Number($(this).data('char-pos'));
          if (words[currentWordIndex][charPos] !== $(this).val().toUpperCase()) {
            $(this).val('');
          }
        });
      });

});