;(function () {
    'use strict';

    /* BEGIN: ORIGINAL CODE COPY */
    function copyTextToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(textToCopy);
        } else {
            let textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "absolute";
            textArea.style.opacity = "0";
            textArea.style.left = "-999999px";
            textArea.style.top = "-999999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            document.execCommand('copy');
            textArea.remove();
        }
    }

    function findOriginalCodeCopyButtonClick(e) {
        let buttonElement = e.target;

        while (buttonElement != null) {
            if ((buttonElement.tagName == 'BUTTON') && (buttonElement.classList.contains('original-code-copy'))) {
                break;
            }

            buttonElement = buttonElement.parentElement;
        }

        copyTextToClipboard(decodeURIComponent(buttonElement.dataset.originalCode));
    }

    function findOriginalCodeCopyButtons() {
        let buttonElements = document.querySelectorAll('button.original-code-copy')

        buttonElements.forEach(
            function (buttonElement) {
                buttonElement.addEventListener('click', findOriginalCodeCopyButtonClick);
            }
        );
    }
    /* END:   ORIGINAL CODE COPY */

    /* BEGIN: HEADER RESIZE ON DOCUMENT SCROLL */
    function windowScrollYInRem() {
        let pixelsPerRem = parseFloat(getComputedStyle(document.documentElement).fontSize)

        return Math.round(window.scrollY / pixelsPerRem);
    }

    function onDocumentScroll(e) {
        document.body.dataset.scrollY = windowScrollYInRem();
    }
    /* END:   HEADER RESIZE ON DOCUMENT SCROLL */

    function onDocumentComplete() {
        document.body.dataset.scrollY = windowScrollYInRem();
        document.addEventListener('scroll', onDocumentScroll);
        findOriginalCodeCopyButtons();
    }

    function onDocumentReadyStateChange(e) {
        if (document.readyState == "complete") {
            onDocumentComplete();
        }
    }

    document.addEventListener('readystatechange', onDocumentReadyStateChange);
})();
