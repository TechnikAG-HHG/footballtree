var best_scorer_players = null;

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
                    console.log("updatedData[key]:", updatedData[key]);
                    data[key] = updatedData[key];
                }
            }
        })
        .catch((error) => console.error("Error fetching data:", error));

    document.title = data["websiteTitle"];
    document.getElementById("websiteTitle").textContent = data["websiteTitle"];

    await fetch("/best_scorer_data", {
        headers: headers,
    })
        .then((response) => response.json())
        .then((bestScorer) => {
            console.log("Best scorer:", bestScorer);
            best_scorer_players = bestScorer["players"];
        })
        .catch((error) => console.error("Error fetching best scorer:", error));

    setTimeout(function () {
        generateTable();
    }, 0);
}

function redirectTo(path) {
    window.location.href = path;
}

function generateTable() {
    var tablesContainer = document.getElementById("tablesContainer");
    let table = document.getElementById("bestScorerTable");
    if (table) {
        table.remove();
    }
    table = document.createElement("table");
    table.id = "bestScorerTable";

    tablesContainer.appendChild(table);

    var tableHead = document.createElement("thead");
    var headRow = document.createElement("tr");

    var positionHead = document.createElement("td");
    positionHead.textContent = "Position";
    headRow.appendChild(positionHead);

    var nameHead = document.createElement("td");
    nameHead.textContent = "Name";
    headRow.appendChild(nameHead);

    var teamHead = document.createElement("td");
    teamHead.textContent = "Team";
    headRow.appendChild(teamHead);

    var goalsHead = document.createElement("td");
    goalsHead.textContent = "Goals";
    headRow.appendChild(goalsHead);

    tableHead.appendChild(headRow);
    table.appendChild(tableHead);

    var tableBody = document.createElement("tbody");

    for (var i = 1; i < Object.keys(best_scorer_players).length + 1; i++) {
        let player = best_scorer_players[`${i}`];
        var row = document.createElement("tr");

        var position = document.createElement("td");
        position.textContent = i;
        row.appendChild(position);

        var name = document.createElement("td");
        name.textContent = player["playerName"];
        row.appendChild(name);

        var team = document.createElement("td");
        team.textContent = player["teamName"];
        row.appendChild(team);

        var goals = document.createElement("td");
        goals.textContent = player["goals"];
        row.appendChild(goals);

        tableBody.appendChild(row);
    }

    table.appendChild(tableBody);
}

document.getElementById("returnButton").addEventListener("click", function () {
    redirectTo("/");
});

updateData();
setInterval(updateData, 5000);
