var tippingData = {};

async function updateData() {
    // Include the last data version in the request headers
    var headers = new Headers();
    headers.append("Last-Data-Update", data["LastUpdate"]);

    fetch("/update_data", {
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

    await fetch("/tipping_data", {
        method: "GET",
    })
        .then((response) => response.json())
        .then((updatedtippingData) => {
            console.log("Updated tipping data:", updatedtippingData);
            tippingData = updatedtippingData;
        })
        .catch((error) => console.error("Error fetching tipping data:", error));

    document.title = data["websiteTitle"];
    document.getElementById("websiteTitle").textContent = data["websiteTitle"];

    console.log("Tipping data:", tippingData);

    if (currentlyTyping == false && tippingData["name"] != null) {
        document.getElementById("name-input").value = tippingData["name"];
    }

    await generateDropdownData();
}

function generateDropdownData() {
    var dropdown = document.getElementById("game-select");

    // Store the currently selected value
    var selectedValue = dropdown.value;

    while (dropdown.firstChild) {
        dropdown.removeChild(dropdown.firstChild);
    }

    var disabledOptions = [];
    var enabledOptions = [];

    for (var i = 0; i < data["Matches"].length; i++) {
        let group;
        var option = document.createElement("option");
        matchData = data["Matches"][i];

        if (
            data["activeMatchNumber"] < -1 ||
            i < data["activeMatchNumber"] + 1
        ) {
            option.style.color = "gray";
            disabledOptions.push(option);
        } else {
            enabledOptions.push(option);
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

        // Set the selected option if it matches the currently selected value
        if (option.textContent === selectedValue) {
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
            group = `${i + 1}. Halbfinale`;
        } else if (i == 2) {
            group = "Spiel um Platz 3";
        } else if (i == 3) {
            group = "Finale";
        } else {
            group = "Nicht definiert";
        }

        option.textContent = `${group}: ${matchData[0]} vs ${matchData[1]}`;

        if (Math.abs(data["activeMatchNumber"]) > i + 1) {
            option.style.color = "gray";
            disabledOptions.push(option);
        } else {
            enabledOptions.push(option);
        }

        // Set the selected option if it matches the currently selected value
        if (option.textContent === selectedValue) {
            option.selected = true;
        }
    }

    // Append the enabled options first
    enabledOptions.forEach((option) => {
        dropdown.appendChild(option);
    });

    // Add a dividing line between disabled and enabled options
    var divider = document.createElement("option");
    divider.disabled = true;
    divider.textContent =
        "------------ Bereits gespielt oder im Gange ------------";
    dropdown.appendChild(divider);

    // Append the disabled options last
    disabledOptions.forEach((option) => {
        dropdown.appendChild(option);
    });

    // If the previously selected option is disabled, select the first enabled option
    if (dropdown.value === selectedValue && dropdown.selectedIndex === -1) {
        dropdown.selectedIndex = 0;
    }
}

function voteForMatch(match) {
    let matchPlayed = false;
    var matchNumber = match.split(".")[0] - 1;
    var matchData = data["Matches"][matchNumber];

    if (match.split(".")[1]) {
        if (match.split(".")[1].startsWith(" Halbfinale")) {
            matchNumber = parseInt(match.split(".")[0]) * -1 - 1;
            console.log("Voting for match", matchNumber);
            matchData = data["finalMatches"][Math.abs(matchNumber) - 2];
        }
    } else if (match.split(":")[0] == "Spiel um Platz 3") {
        matchNumber = -4;
        matchData = data["finalMatches"][2];
    } else if (match.split(":")[0] == "Finale") {
        matchNumber = -5;
        matchData = data["finalMatches"][3];
    }

    if (data["activeMatchNumber"] < -1) {
        if (matchNumber > data["activeMatchNumber"] - 1) {
            matchPlayed = true;
            console.log("Match played");
        }
    } else if (matchNumber < data["activeMatchNumber"] + 1) {
        matchPlayed = true;
        console.log("Match played");
    }

    let voteContainer = document.getElementById("vote-container");
    if (voteContainer != null) {
        voteContainer.remove();
    }

    voteContainer = document.createElement("div");
    voteContainer.id = "vote-container";
    voteContainer.classList.add("vote-container");
    if (matchPlayed) {
        voteContainer.classList.add("disabled");
    }

    let title = document.createElement("h2");
    title.textContent = "Deine Wette für das Spiel:";
    title.classList.add("vote-title");
    voteContainer.appendChild(title);

    let teamsDiv = document.createElement("div");
    teamsDiv.classList.add("teams");
    voteContainer.appendChild(teamsDiv);

    let team1Div = document.createElement("div");
    team1Div.classList.add("names");
    teamsDiv.appendChild(team1Div);

    let team1 = document.createElement("p");
    team1.classList.add("team");
    team1.textContent = matchData[0];
    team1Div.appendChild(team1);

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
    if (tippingData["tips"] != null) {
        if (tippingData["tips"][matchNumber] != null) {
            goals1.value = tippingData["tips"][matchNumber]["team1Goals"];
        }
    }
    if (matchPlayed) {
        goals1.disabled = true;
        goals1.classList.add("disabled");
    }

    team1Div.appendChild(goals1);

    let vs = document.createElement("p");
    vs.textContent = "vs";
    vs.classList.add("vs");
    teamsDiv.appendChild(vs);

    let team2Div = document.createElement("div");
    team2Div.classList.add("names");
    teamsDiv.appendChild(team2Div);

    let team2 = document.createElement("p");
    team2.classList.add("team");
    team2.textContent = matchData[1];
    team2Div.appendChild(team2);

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
    if (tippingData["tips"] != null) {
        if (tippingData["tips"][matchNumber] != null) {
            goals2.value = tippingData["tips"][matchNumber]["team2Goals"];
        }
    }
    if (matchPlayed) {
        goals2.disabled = true;
        goals2.classList.add("disabled");
    }
    team2Div.appendChild(goals2);

    let submitButton = document.createElement("button");
    submitButton.textContent = "Wette abschicken";
    submitButton.id = "submit-button";
    if (matchPlayed) {
        submitButton.disabled = true;
        submitButton.classList.add("disabled");
    }
    submitButton.addEventListener("click", handleSubmit);
    voteContainer.appendChild(submitButton);

    let container = document.getElementsByClassName("content")[0];
    container.appendChild(voteContainer);
}

function handleSubmit(event) {
    event.preventDefault();
    var goals1 = document.getElementById("goals1").value;
    var goals2 = document.getElementById("goals2").value;
    var match = document.getElementById("game-select").value;

    console.log("Submitting tipping data for match", match);
    console.log("Goals", goals1, goals2);

    fetch("/send_tipping_data", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            matchId: match.split(".")[0] - 1,
            team1Goals: goals1,
            team2Goals: goals2,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log("Success:", data);
            updateData();
        })
        .catch((error) => {
            console.error("Error:", error);
        });
}

function redirectTo(path) {
    window.location.href = path;
}

document.getElementById("returnButton").addEventListener("click", function () {
    redirectTo("/");
});

document.getElementById("game-select").addEventListener("change", function () {
    var selectedMatch = document.getElementById("game-select").value;
    voteForMatch(selectedMatch);
});

var typingTimer;
var doneTypingInterval = 500;

var currentlyTyping = false;

document.getElementById("name-input").addEventListener("input", function () {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(function () {
        var name = document.getElementById("name-input").value;
        fetch("/send_user_name", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                userName: name,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log("Success:", data);
            })
            .catch((error) => {
                console.error("Error:", error);
            });
        currentlyTyping = false;
    }, doneTypingInterval);
});

document.getElementById("name-input").addEventListener("keydown", function () {
    clearTimeout(typingTimer);
    currentlyTyping = true;
});

updateData();
setInterval(updateData, 5000);
