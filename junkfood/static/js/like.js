$(document).ready(function () {
    $('.like-form').submit(function (e) {
        e.preventDefault()
        const transcript_id = $(this).attr('id')
        const likeText = $(".like-btn" + transcript_id).find("i").hasClass("fa-heart-o") ? "Unlike" : "Like"
        const trim = $.trim(likeText)
        const url = $(this).attr('action')
        $.ajax({
            type: 'GET',
            url: url,
            success: function (response) {
                if (trim === 'Unlike') {
                    $(`.like-btn${transcript_id}`).html('<i class="fa fa-heart" aria-hidden="true"></i>')
                } else {
                    $(`.like-btn${transcript_id}`).html('<i class="fa fa-heart-o" aria-hidden="true"></i>')
                }
            },
            error: function (response) {
                console.log('error', response)
            }
        })
    });
});
