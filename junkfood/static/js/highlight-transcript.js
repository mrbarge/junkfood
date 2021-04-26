function setupHighlightTranscript(searchTerm) {
    document.addEventListener('DOMContentLoaded', () => {

        // Highlight search terms
        var instance = new Mark(document.querySelector("div.transcript"));
        var searchStr = $('<textarea />').html(searchTerm).text();
        var myRegexp = /[^\s"]+|"([^"]*)"/gi;
        var searchTerms = [];
        var markOptions = {
            "separateWordSearch": false
        };
        do {
            var match = myRegexp.exec(searchStr);
            if (match != null) {
                searchTerms.push(match[1] ? match[1] : match[0]);
            }
        } while (match != null);

        var arrayLength = searchTerms.length;
        for (var i = 0; i < arrayLength; i++) {
            instance.mark(searchTerms[i], markOptions);
        }
    });
}
