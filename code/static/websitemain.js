// Function to handle button clicks and redirect
function redirectTo(path) {
    window.location.href = path;
}

function updateData() {
    // Include the last data version in the request headers
    var headers = new Headers();
    headers.append("Last-Data-Update", data["LastUpdate"]);

    fetch("/update_data", {
        headers: headers,
    })
        .then((response) => response.json())
        .then((updatedData) => {
            console.log("Updated data:", updatedData);
            for (var key in data) {
                if (updatedData.hasOwnProperty(key)) {
                    data[key] = updatedData[key];
                }
            }
        })
        .catch((error) => console.error("Error fetching data:", error));

    document.title = data["websiteTitle"];
    document.getElementById("websiteTitle").textContent = data["websiteTitle"];
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

window.addEventListener("load", function () {
    document.title = data["websiteTitle"];
    document.getElementById("websiteTitle").textContent = data["websiteTitle"];
});

setInterval(updateData, 5000);
