// Assuming 'iframeElement' is a reference to your iframe
var iframe = document.querySelector("iframe");
var iframeDocument = iframe.contentDocument || iframe.contentWindow.document;

// Select and remove #returnButton within the iframe
var returnButton = iframeDocument.querySelector(".header #returnButton");
if (returnButton) {
    returnButton.remove();
}
