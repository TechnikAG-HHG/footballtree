// Function to handle button clicks and redirect
function redirectTo(path) {
    window.location.href = path;
}

// Add click event listeners to the buttons
document.getElementById("planButton").addEventListener("click", function () {
    redirectTo("/plan");
});

document.getElementById("groupButton").addEventListener("click", function () {
    redirectTo("/group");
});

document.getElementById("treeButton").addEventListener("click", function () {
    redirectTo("/tree");
});
