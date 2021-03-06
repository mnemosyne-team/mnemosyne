const MAX_ATTEMPTS = 3;
let attempt = 0;
let words = [];
let trainedWords = {successfullyTrainedWords: [], unsuccessfullyTrainedWords: []};
let currentWordIndex = 0;
let isCorrectlyPronounced = false;
let isRecording = false;

function createMediaRecorder(stream) {
    const audioContext = new AudioContext;
    const input = audioContext.createMediaStreamSource(stream);
    const recorder = new Recorder(input, {
        numChannels: 1
    });

    return { recorder, stream };
}

async function transcribe(audio_data) {
    const formData = new FormData();
    const fileName = new Date().toISOString();
    formData.append('audio_data', audio_data, fileName);

    const response = await fetch(`${window.location.href}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': Cookies.get('csrftoken')
        },
        body: formData
    });

    try {
        const data = await response.json();
        return data.RecognitionStatus === 'Success' ? data : null;
    } catch (error) {
        return null;
    }
}

function checkPronunciation(pronunciation) {
   transcribe(pronunciation)
       .then(result => {
           $('.preloader-wrapper').toggleClass('active');
           const userWordObj = $('.userWord');
           userWordObj.removeClass('correct');
           userWordObj.removeClass('incorrect');
           if (result) {
               const userWord = result.NBest[0].Lexical;
               const word = words[currentWordIndex].word;
               if (userWord === word) {
                   trainedWords.successfullyTrainedWords.push(word);
                   userWordObj.addClass('correct');
                   isCorrectlyPronounced = true;
                   const wordProgress = words[currentWordIndex].study_progress;
                   if (wordProgress < 100) {
                       updateWordProgress(wordProgress + 25);
                       saveWordsProgress([{word, isSuccessfullyTrained: true}])
                   }
               } else {
                   userWordObj.addClass('incorrect');
                   if (attempt >= MAX_ATTEMPTS) {
                       $('.pronunciation').css('visibility', 'visible');
                       const currentWord = words[currentWordIndex];
                       const currentWordProgress = currentWord.study_progress;
                       if (currentWordProgress > 0) {
                           updateWordProgress(currentWordProgress - 25);
                           saveWordsProgress([{word: currentWord.word, isSuccessfullyTrained: false}])
                        }
                       trainedWords.unsuccessfullyTrainedWords.push(currentWord.word);
                   } else {
                      $('.record').removeClass('disabled');
                   }
               }
               if (userWord === '') {
                   userWordObj.removeClass('incorrect');
                   userWordObj.text("Can't recognize");
               } else {

                   userWordObj.text(userWord);
               }
           } else {
               userWordObj.text("Can't recognize");
               if (attempt < MAX_ATTEMPTS) {
                   $('.record').removeClass('disabled');
               }
           }
           $('#next').toggleClass('disabled');
           isRecording = false;
       });
}

function updateCard(word) {
    attempt = 0;
    isCorrectlyPronounced = false;
    $('.word').text(word.word);
    $('.userWord').text('');
    $('.record').removeClass('disabled');
    $('.pronunciation').css('visibility', 'hidden');
    updatePronunciation(word);
    initWordProgress(word);
    updateProgressBar(currentWordIndex+1, words.length);
    updateWordNum(currentWordIndex+1, words.length);
}

$(document).ready(() => {

    document.addEventListener('keydown', function (event) {
        let button = null;
        console.log('---1');
        if (!isRecording) {
            console.log('---2');
            if (event.keyCode === 13) {
                console.log('---3');
                event.preventDefault();
                button = $('#next');
            } else if (event.keyCode === 32 && attempt < MAX_ATTEMPTS && !isCorrectlyPronounced) {
                console.log('---4');
                event.preventDefault();
                button = $('.record');
            }
        }
        if (button) {
            console.log('---5');
            button.focus();
            button.trigger('click');
        }
    });

    $('.pronunciation-audio').click(event => {
        event.preventDefault();
        playAudio($(event.currentTarget).data('pronunciation-url'));
    });

    let wordsetId = $('input[name="category"]').val();

    getUserWords(wordsetId)
      .then(userWords => {
          const trainingContent = $('.container > .row > .col');
          if (userWords.length > 0) {
            words = userWords;
            updateCard(words[currentWordIndex]);
          } else {
              trainingContent.html('<h5 class="center">You have no words to train</h5>');
          }
          trainingContent.css('visibility', 'visible');
      });

    $('#next').click(event => {
        if (!isRecording) {
            if (!isCorrectlyPronounced && attempt < MAX_ATTEMPTS) {
                const word = words[currentWordIndex].word;
                trainedWords.unsuccessfullyTrainedWords.push(word);
                saveWordsProgress([{word, isSuccessfullyTrained: false}])
            }
            if (currentWordIndex < words.length-1) {
                currentWordIndex++;
                updateCard(words[currentWordIndex]);
            } else if (currentWordIndex >= words.length - 1) {
                showResults(trainedWords);
            }
        }

    });

    navigator.mediaDevices.getUserMedia({audio:true, video: false})
        .then(stream => createMediaRecorder(stream))
        .then(({recorder, stream}) => {
            $('.record').click(event => {
                if (!isRecording && !isCorrectlyPronounced && attempt < MAX_ATTEMPTS) {
                    $('#next').toggleClass('disabled');
                    $(event.currentTarget).addClass('disabled pulse');
                    $('.userWord').text('');
                    recorder.record();
                    isRecording = true;
                    attempt++;
                    setTimeout(() => {
                        recorder.stop();
                        $('.record').removeClass('pulse');
                        $('.preloader-wrapper').toggleClass('active');
                        recorder.exportWAV(checkPronunciation);
                        recorder.clear();
                    }, 3000);
                }
            });
        });
});
