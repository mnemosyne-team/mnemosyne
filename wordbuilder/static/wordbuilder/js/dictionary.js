function playAudio(src) {
    const audio = document.createElement('audio');
    $(audio).attr('src', src);
    audio.play();
}

function handlePronunciation(event) {
    playAudio(event.currentTarget.dataset.pronunciationUrl);
}

function init() {


    const modal = new Vue({
        el: '#word-modal',
        data: {
            word: '',
        },
        methods: {
           handlePronunciation: function (event) {
               event.stopPropagation();
               handlePronunciation(event);
           },
            submit: function (event) {
                // const senseId = $('#word-modal form input[type="radio"]:checked').data('sense-id');
                $('#word-modal form')[0].submit();
            }
        },
        mounted: function () {
            this.$nextTick(function () {
                $('.modal').modal();
            });
        }
    });

    $('.collapsible').collapsible();

    $('.tooltipped').tooltip({margin: -10});

    $('.pronunciation').click((event) => {handlePronunciation(event);});

    $('a.delete').click((event) => {
        const wordEntryId = $(event.currentTarget).data('item-id');
        const userWordId = $(event.currentTarget).data('user-word-id');

        fetch(`${window.location.origin}/user_words/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken')
            },
            body: JSON.stringify({'userWordId': userWordId})
        }).then(response => console.log(response));

        $(`#${wordEntryId}`).fadeTo("slow", 0.01, function () {
            $(this).slideUp(250, function () {
                $(this).remove();
            });
        });
    });

    $('form').submit((event) => {
        event.preventDefault();
        const word = $('#word-search').val();

        fetch(`${window.location.origin}/words/${word}/`).
            then(response => {
                if (!response.ok) {
                    throw Error(response.statusText);
                }
                return response.json()
            }).
            then(data => {
                const modalInstance = M.Modal.getInstance($('.modal')[0]);
                modal.word = data;
                modalInstance.open();
            }).
            catch(error => {
                $('#word-search').val('');
                M.toast({html: 'Word not found', classes: 'red lighten-2'});
            });
    });
}

$(document).ready(function() {
    init();
});