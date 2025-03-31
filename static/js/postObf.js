$(document).ready(function() {
    $("pre code").each(function (index, element) {
        var lines = $(element).text().split('\n');
        var numberedLines = lines.map(function (line) {
            return '<span class="line">' + line + '</span>';
        });
        $(element).html(numberedLines.join('\n'));
    });

    // Copy Code functionality
    $('.copy-code-button').on('click', function() {
        const codeBlock = $(this).closest('.code-container').find('code').get(0);
        const range = document.createRange();
        range.selectNode(codeBlock);
        window.getSelection().removeAllRanges(); 
        window.getSelection().addRange(range);

        try {
            const successful = document.execCommand('copy');
            const msg = successful ? 'successful' : 'unsuccessful';
            if (successful) {
                $(this).text('Copied');
            }
        } catch (err) {
            console.log('Oops, unable to copy');
        }

        window.getSelection().removeAllRanges();
    });
});
