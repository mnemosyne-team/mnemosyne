let words = [];
let allDefinitions = [];
let roundDefinitions = [];
let trainedWords = {successfullyTrainedWords: [], unsuccessfullyTrainedWords: []};
let extraDefinitions = [
    'an intense feeling of deep affection',
    'a person who attacks and robs ships at sea',
    'a machine for printing text or pictures, especially one linked to a computer'
]; // to use when user has less than 3 words, so the choice buttons are not empty
let currentWordIndex = 0;
let SYMBOL_START = 65;


$(document).ready(() => {
  $('#next').toggle();

  $('.answer').click(event => {
      let currentWord = words[currentWordIndex];
      let pickedDefinitionIndex = event.currentTarget.value;
      let correctDefinitionIndex = roundDefinitions.indexOf(currentWord.sense.definitions[0]);
      let pickedDefinition = roundDefinitions[pickedDefinitionIndex];
      let word = currentWord.word.toUpperCase();

      $(`#option-${correctDefinitionIndex}`).css("background-color", "#33cc33");

      if (currentWord.sense.definitions[0] === pickedDefinition) {
          saveWordsProgress([{word, isSuccessfullyTrained: true}]);
          if (currentWord.study_progress < 100) {
              updateWordProgress(currentWord.study_progress + 25);
          }
          trainedWords.successfullyTrainedWords.push(word);
      } else {
          saveWordsProgress([{word, isSuccessfullyTrained: false}]);
          if (currentWord.study_progress > 0) {
              updateWordProgress(currentWord.study_progress - 25);
          }
          $(`#option-${pickedDefinitionIndex}`).css("background-color", "#ff8080");
          trainedWords.unsuccessfullyTrainedWords.push(word);
      }
      toggleButtons();
  });

  $('#next').click(event => {
    if (currentWordIndex < words.length - 1) {
      currentWordIndex++;
      const currentWord = words[currentWordIndex];
      toggleButtons();
      updateCard(currentWord);
      currentTypoCount = 0;
    } else if (currentWordIndex === words.length - 1) {
      showResults(trainedWords);
    }
  });

  document.addEventListener('keydown', function (event) {
      if (event.keyCode === 13) {
          const answer = $('.answer');

          if (answer.css('display') !== 'inline-block') {
              $('#next').trigger('click');
          }

      } else if (event.keyCode === 65) {
          const answer = $('.answer');

          if (answer.css('display') === 'inline-block') {
              $('.answer#btn-0').trigger('click');
          }

      } else if (event.keyCode === 66) {
          const answer = $('.answer');

          if (answer.css('display') === 'inline-block') {
              $('.answer#btn-1').trigger('click');
          }

      } else if (event.keyCode === 67) {
          const answer = $('.answer');

          if (answer.css('display') === 'inline-block') {
              $('.answer#btn-2').trigger('click');
          }

      } else if (event.keyCode === 68) {
          const answer = $('.answer');

          if (answer.css('display') === 'inline-block') {
              $('.answer#btn-3').trigger('click');
          }
      }
  });

  function toggleButtons() {
    $('#next').toggle();
    $('.answer').toggle();
  }

  function updateCard(word) {
    roundDefinitions = [];
    $('.options').remove();
    allDefinitions.sort(function() { return 0.5 - Math.random() });
    let correctDefinition = word.sense.definitions[0];
    roundDefinitions.push(correctDefinition);

    let correctIndex = allDefinitions.indexOf(correctDefinition);
    if (correctIndex > -1) {
       allDefinitions.splice(correctIndex, 1);
    }

    roundDefinitions = roundDefinitions.concat(allDefinitions.slice(0, 3));
    roundDefinitions.sort(function() { return 0.5 - Math.random() });

    allDefinitions.push(correctDefinition);

    initWordProgress(word);
    updateProgressBar(currentWordIndex+1, words.length);
    updateWordNum(currentWordIndex+1, words.length);
    $('.name').text(word.word);
    $('#definitions').text(function () {
        for (let i in roundDefinitions) {
            $('#definitions').append(`<tr class="options" id="option-${i}"><th>${String.fromCharCode(SYMBOL_START + +i)}</th><td>${roundDefinitions[i]}</td></tr>`)
        }
    });
  }

  let wordsetId = $('input[name="category"]').val();

  getUserWords(wordsetId)
      .then(userWords => {
          if (userWords.length > 0) {
              words = userWords;
              for(let word in words) {
                  allDefinitions.push(words[word]['sense']['definitions'][0]);
              }
              allDefinitions = allDefinitions.concat(extraDefinitions);
              updateCard(words[currentWordIndex]);
          } else {
              $('.container .col').html('<h5 class="center">You have no words to train</h5>');
          }
      });
});