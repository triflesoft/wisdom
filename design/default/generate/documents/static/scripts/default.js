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

    function configureOriginalCodeCopyButtons() {
        let buttonElements = document.querySelectorAll('button.original-code-copy')

        buttonElements.forEach(
            function (buttonElement) {
                buttonElement.addEventListener('click', findOriginalCodeCopyButtonClick);
            }
        );
    }
    /* END:   ORIGINAL CODE COPY */

    /* BEGIN: HEADER RESIZE ON DOCUMENT SCROLL */
    let headerElement = null;
    let headerResizeThresholdSmall = 1;
    let headerResizeThresholdLarge = 1;

    function onDocumentScroll(e) {
        if (window.scrollY > headerResizeThresholdLarge) {
            headerElement.dataset.isLarge = "no";
        } else if (window.scrollY < headerResizeThresholdSmall) {
            headerElement.dataset.isLarge = "yes";
        }
    }

    function configureHeader() {
        headerElement = document.querySelector('header');

        let headerElementHeight = parseInt(window.getComputedStyle(headerElement).height)
        headerResizeThresholdSmall = 1 * headerElementHeight;
        headerResizeThresholdLarge = 5 * headerElementHeight;

        onDocumentScroll(null);
        document.addEventListener('scroll', onDocumentScroll);
    }
    /* END:   HEADER RESIZE ON DOCUMENT SCROLL */

    function onDocumentComplete() {
        configureHeader();
        configureOriginalCodeCopyButtons();
    }

    function onDocumentReadyStateChange(e) {
        if (document.readyState == "complete") {
            onDocumentComplete();
        }
    }

    document.addEventListener('readystatechange', onDocumentReadyStateChange);
})();
