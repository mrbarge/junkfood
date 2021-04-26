function setupPlyr() {
    const player = new Plyr(document.getElementById('js-player'));
    window.player = player;

    document.addEventListener('DOMContentLoaded', () => {
        // Bind event listener
        function on(selector, type, callback) {
            document.querySelector(selector).addEventListener(type, callback, false);
        }

        // Bind event listener
        function on(selector, type, callback) {
            document.querySelector(selector).addEventListener(type, callback, false);
        }

        $(document).ready(() => {
            $('.player-src').on('click', function () {
                loadMedia($(this).data("src"), $(this).data("episode"), true);
            });
        });
    });
}

function loadMedia(source, episode, play) {
    console.log(source);
    window.player.source = {
        type: 'audio',
        title: episode,
        sources: [
            {
                src: source,
                type: 'audio/mp3',
            }
        ],
    };
    if (play) {
        window.player.play();
    }
}

