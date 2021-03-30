;(function () {
    'use strict';

    /* BEGIN: HEADER */
    let headerElement = null;
    let headerResizeThresholdSmall = 1;
    let headerResizeThresholdLarge = 1;

    function onDocumentScroll(e) {
        if (window.scrollY > headerResizeThresholdLarge) {
            headerElement.dataset.isLarge = 'no';
        } else if (window.scrollY < headerResizeThresholdSmall) {
            headerElement.dataset.isLarge = 'yes';
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
    /* END:   HEADER */

    /* BEGIN: ORIGINAL CODE COPY BUTTONS */
    function copyTextToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(textToCopy);
        } else {
            let textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'absolute';
            textArea.style.opacity = '0';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
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
    /* END:   ORIGINAL CODE COPY BUTTONS */

    /* BEGIN: DATA TABLES */
    function dataTableThClick(e) {
        let thElement = e.target;

        while (thElement != null) {
            if (thElement.tagName == 'TH') {
                break;
            }

            thElement = thElement.parentElement;
        }

        let sortColumn = Array.prototype.indexOf.call(thElement.parentElement.children, thElement);
        let sortDirection = 'asc';
        let tableElement = thElement;

        while (tableElement != null) {
            if (tableElement.tagName == 'TABLE') {
                break;
            }

            tableElement = tableElement.parentElement;
        }

        if (tableElement.dataset.sortColumn == sortColumn) {
            if (tableElement.dataset.sortDirection == 'desc') {
                sortDirection = 'asc';
            } else {
                sortDirection = 'desc';
            }
        }

        tableElement.dataset.sortColumn = sortColumn;
        tableElement.dataset.sortDirection = sortDirection;

        if ((sortColumn > 0) || (sortDirection != 'asc')) {
            tableElement.className = 'data-table sorted-' + (sortColumn + 1) + '-' + sortDirection;
        } else {
            tableElement.className = 'data-table';
        }

        let tbodyElement = tableElement.tBodies[0];
        let rows = Array.prototype.slice.call(tbodyElement.rows);

        if (sortDirection == "asc") {
            rows.sort(function(a, b) { return a.children[sortColumn].dataset.sortOrder > b.children[sortColumn].dataset.sortOrder; });
        } else {
            rows.sort(function(a, b) { return b.children[sortColumn].dataset.sortOrder > a.children[sortColumn].dataset.sortOrder; });
        }

        for(var i = 0; i < rows.length; i++) {
            var detachedRow = tbodyElement.removeChild(rows[i]);

            tbodyElement.appendChild(detachedRow);
        }
    }

    function configureDataTables() {
        let thElements = document.querySelectorAll('table.data-table > thead > tr > th, table.data-table > tfoot > tr > th')

        thElements.forEach(
            function (thElement) {
                thElement.addEventListener('click', dataTableThClick);
            }
        );
    }
    /* END:   DATA TABLES */

    function onDocumentComplete() {
        configureHeader();
        configureOriginalCodeCopyButtons();
        configureDataTables();
    }

    function onDocumentReadyStateChange(e) {
        if (document.readyState == 'complete') {
            onDocumentComplete();
        }
    }

    document.addEventListener('readystatechange', onDocumentReadyStateChange);
})();

