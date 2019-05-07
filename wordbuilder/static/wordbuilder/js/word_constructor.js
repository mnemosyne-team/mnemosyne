let words = [];
let trainedWords = {successfullyTrainedWords: [], unsuccessfullyTrainedWords: []};
let currentWordIndex = 0;
const MAX_TYPOS = 3;
let currentTypoCount = 0;


$(document).ready(() => {

  $('.pronunciation-audio').click(event => {
      playAudio($('.pronunciation-audio').data('pronunciation-url'));
  });


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

  $('#show-answer').click(event => {
    const currentWord = words[currentWordIndex];
    const word = currentWord.word.toUpperCase();

    $($('.char-input')[0]).attr('readonly', true);
    for (let letterIndex in word) {
      const charInput = $(`input#char-${letterIndex}`);
      charInput.val(word[letterIndex]);
      charInput.addClass('valid');
    }
    currentTypoCount = MAX_TYPOS;
    saveWordsProgress([{word, isSuccessfullyTrained: false}]);

    if (currentWord.study_progress < 100 && currentTypoCount < MAX_TYPOS) {
        updateWordProgress(currentWord.study_progress + 25);
    } else if (currentWord.study_progress > 0 && currentTypoCount >= MAX_TYPOS) {
        updateWordProgress(currentWord.study_progress - 25);
    }

    toggleButtons();
    if (currentWord.pronunciation) {
      showPronunciation();
      playAudio($('.pronunciation-audio').data('pronunciation-url'));
    }

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

    const currentWord = words[currentWordIndex];
    const word = currentWord.word.toUpperCase();

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
            if (currentWord.pronunciation) {
              showPronunciation();
              playAudio($('.pronunciation-audio').data('pronunciation-url'));
            }

            toggleButtons();

            if (currentWord.study_progress < 100 && currentTypoCount < MAX_TYPOS) {
              updateWordProgress(currentWord.study_progress + 25);
            } else if (currentWord.study_progress > 0 && currentTypoCount >= MAX_TYPOS) {
              updateWordProgress(currentWord.study_progress - 25);
            }

            const isSuccessfullyTrained = currentTypoCount < MAX_TYPOS;
            saveWordsProgress([{word, isSuccessfullyTrained}]);
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
      hidePronunciation();
      updateCard(currentWord);
      currentTypoCount = 0;
    } else if (currentWordIndex === words.length - 1) {
      showResults(trainedWords);
    }
  });

  function showPronunciation() {
    const pronunciation = $('.pronunciation');
    if (pronunciation.css('visibility') !== 'visible') {
      pronunciation.css('visibility', 'visible');
    }
  }

  function hidePronunciation() {
    const pronunciation = $('.pronunciation');
    if (pronunciation.css('visibility') !== 'hidden') {
      pronunciation.css('visibility', 'hidden');
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
    updateProgressBar(currentWordIndex+1, words.length);
    updateWordNum(currentWordIndex+1, words.length);
    $($('.char-input')[0]).attr('readonly', false);
  }

  let wordsetId = $('input[name="category"]').val();

  getUserWords(wordsetId)
      .then(userWords => {
          words = userWords;
          updateCard(words[currentWordIndex]);
          $('.char-input').on('input', function() {
            const charPos = Number($(this).data('char-pos'));
            if (words[currentWordIndex][charPos] !== $(this).val().toUpperCase()) {
              $(this).val('');
            }
          });
      });
});
