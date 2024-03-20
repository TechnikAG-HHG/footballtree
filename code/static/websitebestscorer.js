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

    if (data["bestScorerActive"] != true) {
        redirectTo("/");
    }

    await fetch("/best_scorer_data", {
        headers: headers,
    })
        .then((response) => response.json())
        .then((bestScorer) => {
            console.log("Best scorer:", bestScorer);
            best_scorer_players = bestScorer["players"];
        })
        .catch((error) => console.error("Error fetching best scorer:", error));

    if (
        best_scorer_players != null &&
        best_scorer_players != undefined &&
        best_scorer_players != "" &&
        best_scorer_players !== 0
    ) {
        drawWinnerPodest();
        generateTable();
    } else {
        let no_players = document.getElementById("noPlayers");
        if (!no_players) {
            let tablesContainer = document.getElementById("tablesContainer");

            no_players = document.createElement("p");
            no_players.textContent = "Keine Spieler gefunden";
            no_players.id = "noPlayers";
            tablesContainer.appendChild(no_players);
        }
    }
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
    positionHead.textContent = "Platzierung";
    headRow.appendChild(positionHead);

    var nameHead = document.createElement("td");
    nameHead.textContent = "Name";
    headRow.appendChild(nameHead);

    var teamHead = document.createElement("td");
    teamHead.textContent = "Team";
    headRow.appendChild(teamHead);

    var goalsHead = document.createElement("td");
    goalsHead.textContent = "Tore";
    headRow.appendChild(goalsHead);

    tableHead.appendChild(headRow);
    table.appendChild(tableHead);

    var tableBody = document.createElement("tbody");

    let pos1counter = 0;
    let pos2counter = 0;
    let pos3counter = 0;

    for (var i = 0; i < Object.keys(best_scorer_players).length; i++) {
        let player = best_scorer_players[`${i}`];
        console.log(player);
        console.log(player["rank"]);
        var row = document.createElement("tr");

        var position = document.createElement("td");
        position.textContent = player["rank"];
        row.appendChild(position);

        var name = document.createElement("td");
        name.textContent = player["playerName"];

        if (player["rank"] == 1) {
            document.getElementsByClassName("firstText")[0].textContent =
                player["playerName"];
            pos1counter++;
            name.style.color = "rgb(237, 202, 6)";
            name.style.fontWeight = "bold";
        } else if (player["rank"] == 2) {
            document.getElementsByClassName("secondText")[0].textContent =
                player["playerName"];
            pos2counter++;
            name.style.color = "silver";
            name.style.fontWeight = "bold";
        } else if (player["rank"] == 3) {
            document.getElementsByClassName("thirdText")[0].textContent =
                player["playerName"];
            pos3counter++;
            name.style.color = "#A97142";
            name.style.fontWeight = "bold";
        }

        row.appendChild(name);
        var team = document.createElement("td");
        team.textContent = player["teamName"];
        row.appendChild(team);

        var goals = document.createElement("td");
        goals.textContent = player["goals"];
        row.appendChild(goals);

        tableBody.appendChild(row);
    }

    if (pos1counter > 1) {
        document.getElementsByClassName("firstText")[0].textContent =
            pos1counter + " Spieler...";
    }
    if (pos2counter > 1) {
        document.getElementsByClassName("secondText")[0].textContent =
            pos2counter + " Spieler...";
    }
    if (pos3counter > 1) {
        document.getElementsByClassName("thirdText")[0].textContent =
            pos3counter + " Spieler...";
    }

    table.appendChild(tableBody);
}

function drawWinnerPodest() {
    let podest = document.getElementById("podest");
    if (podest) {
        podest.remove();
    }

    // draw a podest for the first 3 players with svg
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.id = "podest";
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");

    var first = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    first.setAttribute("x", "33%");
    first.setAttribute("y", "40");
    first.setAttribute("width", "33%");
    first.setAttribute("height", "150");
    first.setAttribute("fill", "rgb(237, 202, 6)");
    svg.appendChild(first);

    var second = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    second.setAttribute("x", "0");
    second.setAttribute("y", "90");
    second.setAttribute("width", "33%");
    second.setAttribute("height", "100");
    second.setAttribute("fill", "silver");
    svg.appendChild(second);

    var third = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    third.setAttribute("x", "66%");
    third.setAttribute("y", "140");
    third.setAttribute("width", "33%");
    third.setAttribute("height", "50");
    third.setAttribute("fill", "#A97142");
    svg.appendChild(third);

    var firstText = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "text"
    );
    firstText.setAttribute("x", "49.5%");
    firstText.setAttribute("y", "35"); // adjust this value to position the text correctly
    firstText.textContent = "Erster";
    firstText.classList.add("svgText");
    firstText.classList.add("firstText");
    svg.appendChild(firstText);

    var secondText = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "text"
    );
    secondText.setAttribute("x", "16.5%");
    secondText.setAttribute("y", "85"); // adjust this value to position the text correctly
    secondText.textContent = "Zweiter";
    secondText.classList.add("svgText");
    secondText.classList.add("secondText");
    svg.appendChild(secondText);

    var thirdText = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "text"
    );
    thirdText.setAttribute("x", "82.5%");
    thirdText.setAttribute("y", "135"); // adjust this value to position the text correctly
    thirdText.textContent = "Dritter";
    thirdText.classList.add("svgText");
    thirdText.classList.add("thirdText");
    svg.appendChild(thirdText);

    var podestContainer = document.getElementById("podestContainer");
    podestContainer.appendChild(svg);
}

document.getElementById("returnButton").addEventListener("click", function () {
    redirectTo("/");
});

updateData();
setInterval(updateData, 10000);
