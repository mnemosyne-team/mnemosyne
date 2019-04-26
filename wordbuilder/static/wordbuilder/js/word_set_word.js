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

    $('.tooltipped').tooltip({margin: -5});

    $('.pronunciation').click((event) => {handlePronunciation(event);});

}

function toggle(source) {
    let checkboxes = document.getElementsByName('choices');
    let flag = $(source).val();
    if (flag === 'true') {
        for(let i=0, n=checkboxes.length;i<n;i++) {
            checkboxes[i].checked = true;
        }
        $(source).val('false');
    }
    else {
        for (let i = 0, n = checkboxes.length; i < n; i++) {
            checkboxes[i].checked = false;
        }
        $(source).val('true');
    }
}


$(document).ready(function() {
    init();
});