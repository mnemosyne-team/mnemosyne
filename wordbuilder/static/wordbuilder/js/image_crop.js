$(function () {
    let $image = $("#image");
    let cropBoxData;
    let canvasData;

    $("#id_image").change(function () {
        console.log(this.files);
        if (this.files && this.files[0]) {
            let reader = new FileReader();
            reader.onload = function (e) {
                $("#image").attr("src", e.target.result);
                $("#modalCrop").modal({
                    dismissible: false,
                    onOpenEnd: function () {
                        document.addEventListener('keydown', listener)
                    },
                    onCloseStart: function () {
                        document.removeEventListener('keydown', listener);
                        $image.cropper("destroy");
                    }
                });
                $("#modalCrop").modal('open');
                $image.cropper({
                    viewMode: 1,
                    aspectRatio: 1 / 1,
                    minCropBoxWidth: 200,
                    minCropBoxHeight: 200,
                    guides: false,
                    background: false,
                    zoomable: false,
                    scalable: false,
                    roatable: false,
                    center: false,
                    toggleDragModeOnDblclick: false,
                    ready: function () {
                        $image.cropper("setCanvasData", canvasData);
                        $image.cropper("setCropBoxData", cropBoxData);
                    }
                });
            };
            reader.readAsDataURL(this.files[0]);
        }
    });

    $(".js-crop-and-upload").click(function () {
        let cropData = $image.cropper("getData");
        console.log(cropData);
        $("#id_x").val(cropData["x"]);
        $("#id_y").val(cropData["y"]);
        $("#id_height").val(cropData["height"]);
        $("#id_width").val(cropData["width"]);
        $("#modalCrop").modal('close');
    });

    let listener = function (event) {
        let button = null;
        if (event.keyCode === 13) {
            event.preventDefault();
            button = $('.js-crop-and-upload');
        }
        if (button) {
            button.focus();
            button.trigger('click');
        }
    };
});