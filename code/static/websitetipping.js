async function updateData() {
    // Include the last data version in the request headers
    var headers = new Headers();
    headers.append("Last-Data-Update", data["LastUpdate"]);

    await fetch("/update_data", {
        headers: headers,
    })
        .then((response) => response.json())
        .then((updatedData) => {
            console.log("Updated data:", updatedData);

            // Update variables in JavaScript
            for (var key in updatedData) {
                if (updatedData.hasOwnProperty(key)) {
                    data[key] = updatedData[key];
                }
            }
        })
        .catch((error) => console.error("Error fetching data:", error));

    document.title = data["websiteTitle"];
    document.getElementById("websiteTitle").textContent = data["websiteTitle"];

    await generateDropdownData();
}

function generateDropdownData() {
    var dropdown = document.getElementById("game-select");

    // Store the currently selected value
    var selectedValue = dropdown.value;

    while (dropdown.firstChild) {
        dropdown.removeChild(dropdown.firstChild);
    }

    for (var i = 0; i < data["Matches"].length; i++) {
        let group;
        var option = document.createElement("option");
        matchData = data["Matches"][i];

        if (i < -1 || i < data["activeFinalMatch"] + 1) {
            option.classList.add("disabled");
            option.disabled = true;
        }

        if (matchData[4] == 1) {
            group = "Gruppe A";
        } else if (matchData[4] == 2) {
            group = "Gruppe B";
        } else {
            group = "Gruppe nicht definiert";
        }

        option.textContent = `${i + 1}. ${group}: ${matchData[0]} vs ${
            matchData[1]
        }`;
        dropdown.appendChild(option);

        // If this option is the previously selected one, select it
        if (option.value === selectedValue) {
            option.selected = true;
        }
    }

    if (data["finalMatches"] == null || data["finalMatches"].length == 0) {
        return;
    }

    for (var i = 0; i < data["finalMatches"].length; i++) {
        if (
            data["finalMatches"][i][0] == null ||
            data["finalMatches"][i][1] == null
        ) {
            continue;
        }

        let group;
        var option = document.createElement("option");
        matchData = data["finalMatches"][i];

        if (i == 0 || i == 1) {
            group = "Halbfinale";
        } else if (i == 2) {
            group = "Spiel um Platz 3";
        } else if (i == 3) {
            group = "Finale";
        } else {
            group = "Nicht definiert";
        }

        option.textContent = `${i + 1}. ${group}: ${matchData[0]} vs ${
            matchData[1]
        }`;
        dropdown.appendChild(option);

        // If this option is the previously selected one, select it
        if (option.value === selectedValue) {
            option.selected = true;
        }
    }
}

function voteForMatch(match) {
    var matchNumber = match.split(".")[0] - 1;
    var matchData = data["Matches"][matchNumber];

    let voteContainer = document.getElementById("vote-container");
    if (voteContainer != null) {
        voteContainer.remove();
    }

    voteContainer = document.createElement("div");
    voteContainer.id = "vote-container";
    voteContainer.classList.add("vote-container");

    let namesDiv = document.createElement("div");
    namesDiv.classList.add("names");
    voteContainer.appendChild(namesDiv);

    let team1 = document.createElement("p");
    team1.classList.add("team");
    team1.textContent = matchData[0];
    namesDiv.appendChild(team1);

    let team2 = document.createElement("p");
    team2.classList.add("team");
    team2.textContent = matchData[1];
    namesDiv.appendChild(team2);

    let entryDiv = document.createElement("div");
    entryDiv.classList.add("entry");

    let goals1 = document.createElement("input");
    goals1.type = "number";
    goals1.id = "goals1";
    goals1.placeholder = "Tore";
    goals1.min = "0";
    goals1.addEventListener("input", function () {
        if (goals1.value < 0) {
            goals1.value = 0;
        }
    });
    entryDiv.appendChild(goals1);

    let goals2 = document.createElement("input");
    goals2.type = "number";
    goals2.id = "goals2";
    goals2.placeholder = "Tore";
    goals2.min = "0";
    goals2.addEventListener("input", function () {
        if (goals2.value < 0) {
            goals2.value = 0;
        }
    });
    entryDiv.appendChild(goals2);

    voteContainer.appendChild(entryDiv);

    let container = document.getElementsByClassName("content")[0];
    container.appendChild(voteContainer);
}

function redirectTo(path) {
    window.location.href = path;
}

document.getElementById("returnButton").addEventListener("click", function () {
    redirectTo("/logout");
});

document.getElementById("game-select").addEventListener("change", function () {
    var selectedMatch = document.getElementById("game-select").value;
    voteForMatch(selectedMatch);
});

updateData();
setInterval(updateData, 5000);
