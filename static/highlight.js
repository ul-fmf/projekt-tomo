function highlightTextArea(id, python) {
    CodeMirror.fromTextArea(id, {
        parserfile: ["../contrib/python/js/parsepython.js"],
        stylesheet: "/static/codemirror/contrib/python/css/pythoncolors.css",
        path: "/static/codemirror/js/",
        lineNumbers: true,
        textWrapping: false,
        indentUnit: 4,
        height: "22.5em",
        parserConfig: {'pythonVersion': python, 'strictErrors': true}
    })
}

function highlightCode(code) {
    new_code = document.createElement("code");
    highlightText(code.textContent, new_code);
    new_code.removeChild(new_code.lastChild);
    code.parentNode.replaceChild(new_code, code);
}

function highlightCodes() {
    var codes = document.getElementsByTagName("code");
    for (var i = 0; i < codes.length; i++) {
        highlightCode(codes[i]);
    }
}

window.onload = highlightCodes

