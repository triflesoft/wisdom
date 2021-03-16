;(function () {
    'use strict';

    function windowScrollYInRem() {
        let pixelsPerRem = parseFloat(getComputedStyle(document.documentElement).fontSize)

        return Math.round(window.scrollY / pixelsPerRem);
    }

    function onComplete() {
        document.body.dataset.scrollY = windowScrollYInRem();

        document.addEventListener(
            'scroll',
            function(e) {
                document.body.dataset.scrollY = windowScrollYInRem();
            }
        );
    }

    document.addEventListener(
        'readystatechange',
        function (e) {
            if (document.readyState == "complete") {
                onComplete();
            }
        }
    );
})();
