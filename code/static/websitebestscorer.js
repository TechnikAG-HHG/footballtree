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
        drawWinnerPodest();
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

function drawWinnerPodest() {
    // draw a podest for the first 3 players with svg
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.id = "podest";
    svg.setAttribute("width", "500");
    svg.setAttribute("height", "500");

    svg.setAttribute("viewBox", "0 0 500 500");

    var first = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    first.setAttribute("x", "200");
    first.setAttribute("y", "0");
    first.setAttribute("width", "100");
    first.setAttribute("height", "500");
    first.setAttribute("fill", "gold");
    svg.appendChild(first);

    var second = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    second.setAttribute("x", "100");
    second.setAttribute("y", "100");
    second.setAttribute("width", "100");
    second.setAttribute("height", "400");
    second.setAttribute("fill", "silver");
    svg.appendChild(second);

    var third = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    third.setAttribute("x", "300");
    third.setAttribute("y", "200");
    third.setAttribute("width", "100");
    third.setAttribute("height", "300");
    third.setAttribute("fill", "brown");
    svg.appendChild(third);

    var podestContainer = document.getElementById("podestContainer");
    podestContainer.appendChild(svg);

    var firstPlayer = document.createElement("p");
    firstPlayer.textContent = best_scorer_players["1"]["playerName"];
    podestContainer.appendChild(firstPlayer);
    var secondPlayer = document.createElement("p");
    secondPlayer.textContent = best_scorer_players["2"]["playerName"];
    podestContainer.appendChild(secondPlayer);
    var thirdPlayer = document.createElement("p");
    thirdPlayer.textContent = best_scorer_players["3"]["playerName"];
    podestContainer.appendChild(thirdPlayer);
}

document.getElementById("returnButton").addEventListener("click", function () {
    redirectTo("/");
});

updateData();
setInterval(updateData, 5000);
