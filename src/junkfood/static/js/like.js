    $(document).ready(function () {
        $('.like-form').submit(function (e) {
            e.preventDefault()
            const transcript_id = $(this).attr('id')
            const likeText = $(".like-btn" + transcript_id).find("i").hasClass("fas fa-heart") ? "Unlike" : "Like"
            const trim = $.trim(likeText)
            const url = $(this).attr('action')
            $.ajax({
                type: 'GET',
                url: url,
                success: function (response) {
                    if (trim === 'Unlike') {
                        $(`.like-btn${transcript_id}`).html('<span style="font-size: 1em; color: tomato;"><i class="far fa-heart" aria-hidden="true"></i></span>')
                    } else {
                        $(`.like-btn${transcript_id}`).html('<span style="font-size: 1em; color: tomato;"><i class="fas fa-heart" aria-hidden="true"></i></span>')
                    }
                },
                error: function (response) {
                    console.log('error', response)
                }
            })
        });
    });
