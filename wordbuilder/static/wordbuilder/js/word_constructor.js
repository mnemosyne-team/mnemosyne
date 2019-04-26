let words = [];
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
  });

  document.addEventListener('keydown', function (event) {
    const word = words[currentWordIndex].word.toUpperCase();

    for (let charInput of $('.char-input')) {
      const charInputObj = $(charInput);

      if (charInputObj.val().length > 0) {
        continue;
      }

      if (charInputObj.val().length === 0) {
        if (String.fromCharCode(event.keyCode) === word[Number(charInputObj.data('char-pos'))]) {
          charInputObj.val(String.fromCharCode(event.keyCode));
          charInputObj.addClass('valid');
          if (Number(charInputObj.data('char-pos')) === word.length - 1) {
            togglePronunciation();
            playAudio($('.pronunciation-audio').data('pronunciation-url'));
            toggleButtons();
            updateWordProgress(words[currentWordIndex]);
            saveWordProgress(word, currentTypoCount < MAX_TYPOS);
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
    }
  });

  function updateWordProgress(word) {
      const wordProgress = $('.word-progress');
      if (word.study_progress < 100 && currentTypoCount < MAX_TYPOS) {
        wordProgress.text(`${word.study_progress + 25}%`);
      } else if (word.study_progress > 0 && currentTypoCount >= MAX_TYPOS) {
        wordProgress.text(`${word.study_progress - 25}%`);
      }
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
  }

  function updatePronunciation(word) {
    $('.pronunciation-spelling').text(`[${word.pronunciation.phonetic_spelling}]`);
    $('.pronunciation-audio').data('pronunciation-url', word.pronunciation.audio);
  }

  function initDefinition(word) {
    $('.definition').text(word.sense.definitions[0]);
  }

  function initWordProgress(word) {
    $('.word-progress').text(`${word.study_progress}%`);
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
      });

});