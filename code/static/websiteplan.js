var matchCount = 0; // Global variable to keep track of the total number of matches
var timeInterval = data["timeInterval"]; // Global variable to keep track of the time interval between matches

var startTime = new Date(); // Set the start time

startTime.setHours(0, 0, 0, 0);

var intervalActivated = false;

function generateTableGroup(matches) {
    if (
        data["Matches"] == null ||
        data["Matches"] == "null" ||
        data["Matches"] == "" ||
        data["Matches"] == "[]" ||
        data["Matches"] === 0
    ) {
        let no_matches = document.getElementById("noMatches");

        console.log("No matches found");

        if (!no_matches) {
            let tablesContainer = document.getElementById("tablesContainer");
            no_matches = document.createElement("p");
            no_matches.textContent = "Keine Spiele gefunden";
            no_matches.id = "noMatches";
            tablesContainer.appendChild(no_matches);
        }
        return;
    }

    let no_matches = document.getElementById("noMatches");
    if (no_matches) {
        no_matches.remove();
    }

    var tablesContainer = document.getElementById("tablesContainer");

    document.title = data["websiteTitle"];
    document.getElementById("websiteTitle").textContent = data["websiteTitle"];

    // If the table already exists, clear its contents
    var table = tablesContainer.querySelector(".tableGroup");
    if (table) {
        var tbody = table.querySelector("tbody");
        while (tbody.firstChild) {
            tbody.removeChild(tbody.firstChild);
        }
    } else {
        // If the table doesn't exist, create it
        table = document.createElement("table");
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");

        table.className = "tableGroup";

        var headerRow = thead.insertRow(0);
        var headerCellTime = headerRow.insertCell(0);
        headerCellTime.textContent = "Zeit";
        headerCellTime.className = "headerCell";

        var headerCellGroup = headerRow.insertCell(1);
        headerCellGroup.textContent = "Spiele";
        headerCellGroup.className = "headerCell";
        headerCellGroup.colSpan = 4;

        var headerCellT = headerRow.insertCell(2);
        headerCellT.textContent = "Tore";
        headerCellT.className = "headerCell";

        table.appendChild(thead);
        table.appendChild(tbody);
        tablesContainer.appendChild(table);
    }

    // Add the new matches to the table
    var i = 0;
    matches.forEach((match) => {
        var row = tbody.insertRow();

        if (i == data["activeMatchNumber"] && data["pauseMode"] == false) {
            row.style.backgroundColor = "black";
        }

        row.id = "section" + (i + 1); // Set the id of the row

        var cellTime = row.insertCell(0);
        var matchTime = new Date(
            startTime.getTime() + i * timeInterval * 60000
        );
        cellTime.textContent = formatTime(matchTime);

        var cellMatchNumber = row.insertCell(1);
        var matchNumber = i + 1;
        cellMatchNumber.textContent = "Spiel " + matchNumber;

        var cellGroup = row.insertCell(2);
        cellGroup.textContent = `Gruppe ${match[4]}`;

        var cellFirstTeam = row.insertCell(3);
        cellFirstTeam.textContent = match[0];

        var cellSecondTeam = row.insertCell(4);
        cellSecondTeam.textContent = match[1];

        if (data["activeMatchNumber"] > i || data["activeMatchNumber"] < 0) {
            if (match[2] > match[3]) {
                cellFirstTeam.className = "style-winner";
                cellSecondTeam.className = "style-loser";
            } else if (match[2] < match[3]) {
                cellSecondTeam.className = "style-winner";
                cellFirstTeam.className = "style-loser";
            } else {
                cellFirstTeam.className = "style-draw";
                cellSecondTeam.className = "style-draw";
            }
        }

        var cellT = row.insertCell(5);
        cellT.textContent = match[2] + " : " + match[3];

        finalMatchesTime = new Date(
            startTime.getTime() + (i + 1) * timeInterval * 60000
        );

        i++;
    });

    setTimeout(function () {
        if (window.innerWidth > 1000) {
            window.location.hash = `section${data["activeMatchNumber"]}`;
        }
    }, 500);
}

function generatePauseTime(time) {
    if (time == 0 || time == null || time == "0") {
        let pauseTimeDiv = document.getElementById("pauseTime");
        if (pauseTimeDiv) {
            pauseTimeDiv.remove();
        }
    }

    oldfinalMatchesTime = finalMatchesTime;
    finalMatchesTime = new Date(finalMatchesTime.getTime() + time * 60000);

    let tablesContainer = document.getElementById("tablesContainer");

    let pauseTimeText = document.getElementById("pauseTimeText");
    let pauseTimeElement = document.getElementById("pauseTimeProgress");
    let pauseTimeStart = document.getElementById("pauseTimeStart");
    let pauseTimeEnd = document.getElementById("pauseTimeEnd");

    if (pauseTimeElement) {
        pauseTimeText.textContent = `Pause ${time} Minuten`;
        pauseTimeStart.textContent = `${formatTime(oldfinalMatchesTime)}`;
        pauseTimeEnd.textContent = `${formatTime(finalMatchesTime)}`;
    } else {
        let pauseTimeDiv = document.createElement("div");
        pauseTimeDiv.className = "pauseTime";

        pauseTimeElement = document.createElement("progress");
        pauseTimeElement.id = "pauseTimeProgress";
        pauseTimeElement.max = time * 60;
        pauseTimeElement.value = 0;

        pauseTimeText = document.createElement("p");
        pauseTimeText.textContent = `Pause ${time} Minuten`;
        pauseTimeText.id = "pauseTimeText";

        pauseTimeStart = document.createElement("p");
        pauseTimeStart.textContent = `${formatTime(oldfinalMatchesTime)}`;
        pauseTimeStart.id = "pauseTimeStart";

        pauseTimeEnd = document.createElement("p");
        pauseTimeEnd.textContent = `${formatTime(finalMatchesTime)}`;
        pauseTimeEnd.id = "pauseTimeEnd";

        pauseTimeDiv.appendChild(pauseTimeStart);
        pauseTimeDiv.appendChild(pauseTimeText);
        pauseTimeDiv.appendChild(pauseTimeEnd);
        pauseTimeDiv.appendChild(pauseTimeElement);
        tablesContainer.appendChild(pauseTimeDiv);
    }

    finalMatchesTime = new Date(
        finalMatchesTime.getTime() - data["timeIntervalFM"] * 60000
    );
}

function updatePauseTime() {
    if (intervalActivated == true) {
        // update the progress bar with the current time and the finalmatchtime
        let pauseTimeElement = document.getElementById("pauseTimeProgress");
        if (pauseTimeElement) {
            //console.log(finalMatchesTime);
            let currentTime = new Date();
            let timeDifference = currentTime - oldfinalMatchesTime;
            let timeDifferenceInSeconds = timeDifference / 1000;
            pauseTimeElement.value = timeDifferenceInSeconds;
            //console.log(timeDifferenceInSeconds);
        }
    }
}

function finalMatchTable() {
    if (
        data["Matches"] == null ||
        data["Matches"] == "null" ||
        data["Matches"] == "" ||
        data["Matches"] == "[]" ||
        data["Matches"] === 0
    ) {
        console.log("No matches found");
        return; // Add return statement here
    }

    if ("finalMatches" in data) {
        if (data["pauseBeforeFM"] != null && data["pauseBeforeFM"] != "0") {
            let requestedtime = parseInt(data["pauseBeforeFM"]);
            generatePauseTime(requestedtime);
        } else {
            let pauseTimeElement =
                document.getElementsByClassName("pauseTime")[0];
            if (pauseTimeElement) {
                pauseTimeElement.remove();
                console.log("Removed pauseTimeElement");
            }
        }

        if (data["pauseMode"] == true && intervalActivated == false) {
            updatePauseTime();
            intervalActivated = true;
        }

        if (data["pauseMode"] == false) {
            let pauseTimeElement = document.getElementById("pauseTimeProgress");

            if (pauseTimeElement) {
                pauseTimeElement.value = 0;
            }

            intervalActivated = false;
        }

        var tablesContainer = document.getElementById("tablesContainer");

        var table = tablesContainer.querySelector(".tableFinalMatches");
        if (table) {
            table.remove();
        }

        table = document.createElement("table");
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");

        table.className = "tableFinalMatches";

        var headerRow = thead.insertRow(0);
        var headerCellTime = headerRow.insertCell(0);
        headerCellTime.textContent = "Zeit";
        headerCellTime.className = "headerCell";

        var headerCellGroup = headerRow.insertCell(1);
        headerCellGroup.textContent = "Finalspiele";
        headerCellGroup.className = "headerCell";
        headerCellGroup.colSpan = 3;

        var headerCellT = headerRow.insertCell(2);
        headerCellT.textContent = "Tore";
        headerCellT.className = "headerCell";

        table.appendChild(thead);
        table.appendChild(tbody);
        tablesContainer.appendChild(table);

        var finalMatches = data["finalMatches"];
        if (finalMatches == null) {
            var finalMatchesSliced = [];
            while (finalMatchesSliced.length < 4) {
                finalMatchesSliced.push(["???", "???", ["0", "0"]]);
            }

            var totalMatchNumber = 4;
        } else {
            if (finalMatches.length > Math.abs(data["activeMatchNumber"]) - 1) {
                if (
                    finalMatches.length / 2 <
                    Math.abs(data["activeMatchNumber"]) - 1
                ) {
                    var finalMatchesSliced = finalMatches;
                } else {
                    var finalMatchesSliced = finalMatches.slice(0, 2);
                }
                while (finalMatchesSliced.length < finalMatches.length) {
                    finalMatchesSliced.push(["???", "???", ["0", "0"]]);
                }
            } else {
                var finalMatchesSliced = finalMatches;
            }

            var totalMatchNumber = finalMatchesSliced.length;
        }

        // Add the new matches to the table
        var i = 1;
        finalMatchesSliced.forEach((match) => {
            var row = tbody.insertRow();

            if (data["activeMatchNumber"] < -1) {
                if (
                    i + 1 == Math.abs(data["activeMatchNumber"]) &&
                    data["pauseMode"] == false
                ) {
                    row.style.backgroundColor = "black";
                }
            }

            row.id = "section" + (i + 1) * -1; // Set the id of the row

            var cellTime = row.insertCell(0);

            if (
                data["timeIntervalFM"] == null ||
                data["timeIntervalFM"] == "0"
            ) {
                var matchTime = new Date(
                    finalMatchesTime.getTime() + i * timeInterval * 60000
                );
            } else {
                var matchTime = new Date(
                    finalMatchesTime.getTime() +
                        i * data["timeIntervalFM"] * 60000
                );
            }

            cellTime.textContent = formatTime(matchTime);

            var cellMatchNumber = row.insertCell(1);
            var matchNumber = i;
            if (i == totalMatchNumber) {
                cellMatchNumber.textContent = "Finale";
            } else if (i == totalMatchNumber - 1) {
                cellMatchNumber.textContent = "Spiel um Platz 3";
            } else {
                cellMatchNumber.textContent = "Halbfinalspiel " + matchNumber;
            }

            var cellFirstTeam = row.insertCell(2);
            cellFirstTeam.textContent = match[0];

            var cellSecondTeam = row.insertCell(3);
            cellSecondTeam.textContent = match[1];

            if (
                Math.abs(data["activeMatchNumber"]) - 1 > i &&
                data["finalMatches"] != null
            ) {
                if (match[2][0] > match[2][1]) {
                    cellFirstTeam.className = "style-winner";
                    cellSecondTeam.className = "style-loser";
                } else if (match[2][0] < match[2][1]) {
                    cellSecondTeam.className = "style-winner";
                    cellFirstTeam.className = "style-loser";
                } else {
                    cellFirstTeam.className = "style-draw";
                    cellSecondTeam.className = "style-draw";
                }
            }

            var cellT = row.insertCell(4);
            cellT.textContent = match[2][0] + " : " + match[2][1];

            i++;
        });
    }
}

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

    startTime.setHours(data["startTime"][0], data["startTime"][1], 0, 0);
    timeInterval = data["timeInterval"];

    document.title = data["websiteTitle"];
    document.getElementById("websiteTitle").textContent = data["websiteTitle"];

    setTimeout(function () {
        generateTableGroup(data["Matches"]);
        finalMatchTable();
    }, 0);
}

function formatTime(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    return (
        (hours < 10 ? "0" : "") +
        hours +
        ":" +
        (minutes < 10 ? "0" : "") +
        minutes +
        " Uhr"
    );
}

// Function to handle button clicks and redirect
function redirectTo(path) {
    window.location.href = path;
}

document.getElementById("returnButton").addEventListener("click", function () {
    redirectTo("/");
});

startTime.setHours(data["startTime"][0], data["startTime"][1], 0, 0);
generateTableGroup(data["Matches"]);
finalMatchTable();

updateData();

// call updateData() every 5 seconds
setInterval(updateData, 10000);
setInterval(updatePauseTime, 100);
