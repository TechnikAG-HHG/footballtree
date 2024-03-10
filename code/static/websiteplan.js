var matchCount = 0; // Global variable to keep track of the total number of matches
var timeInterval = data["timeInterval"]; // Global variable to keep track of the time interval between matches

var startTime = new Date(); // Set the start time
var finalMatchesTime = new Date(); // Set the final matches time
var KOMatchesTime = new Date(); // Set the K.O. matches time

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
            generateFullSize(match, i, row);
        } else {
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

            if (
                data["activeMatchNumber"] > i ||
                data["activeMatchNumber"] < 0
            ) {
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

            KOMatchesTime = new Date(
                startTime.getTime() + (i + 1) * timeInterval * 60000
            );
        }

        i++;
    });
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

function KOMatchTable() {
    if (
        data["Matches"] == null ||
        data["Matches"] == "null" ||
        data["Matches"] == "" ||
        data["Matches"] == "[]" ||
        data["Matches"] === 0
    ) {
        console.log("No matches found");
        finalMatchesTime = new Date(KOMatchesTime.getTime());
        return; // Add return statement here
    }

    if ("KOMatches" in data) {
        var tablesContainer = document.getElementById("tablesContainer");

        var table = tablesContainer.querySelector(".tableKOMatches");
        if (table) {
            table.remove();
        }

        table = document.createElement("table");
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");

        table.className = "tableKOMatches";

        var headerRow = thead.insertRow(0);
        var headerCellTime = headerRow.insertCell(0);
        headerCellTime.textContent = "Zeit";
        headerCellTime.className = "headerCell";

        var headerCellGroup = headerRow.insertCell(1);
        headerCellGroup.textContent = "K.O.-Spiele";
        headerCellGroup.className = "headerCell";
        headerCellGroup.colSpan = 3;

        var headerCellT = headerRow.insertCell(2);
        headerCellT.textContent = "Tore";
        headerCellT.className = "headerCell";

        table.appendChild(thead);
        table.appendChild(tbody);
        tablesContainer.appendChild(table);

        var KOMatches = data["KOMatches"];
        if (KOMatches != null) {
            var i = 100;
            var y = 0;
            KOMatches.forEach((match) => {
                var row = tbody.insertRow();

                if (data["activeMatchNumber"] < -1) {
                    if (
                        i == Math.abs(data["activeMatchNumber"]) &&
                        data["pauseMode"] == false
                    ) {
                        generateFullSize(
                            match,
                            i,
                            row,
                            (gameName = "K.O.-Spiel " + (y + 1))
                        );
                    } else {
                        row.id = "section" + i * -1; // Set the id of the row

                        var cellTime = row.insertCell(0);
                        var matchTime = new Date(
                            KOMatchesTime.getTime() +
                                y * data["timeIntervalFM"] * 60000
                        );
                        cellTime.textContent = formatTime(matchTime);

                        var cellMatchNumber = row.insertCell(1);
                        cellMatchNumber.textContent = "K.O. Spiel " + (y + 1);

                        var cellFirstTeam = row.insertCell(2);
                        cellFirstTeam.textContent = match[0];

                        var cellSecondTeam = row.insertCell(3);
                        cellSecondTeam.textContent = match[1];

                        if (
                            Math.abs(data["activeMatchNumber"]) > i &&
                            data["KOMatches"] != null
                        ) {
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

                        var cellT = row.insertCell(4);
                        cellT.textContent = match[2] + " : " + match[3];
                    }
                }

                i++;
                y++;
            });

            finalMatchesTime = new Date(
                KOMatchesTime.getTime() +
                    (y - 1) * data["timeIntervalFM"] * 60000
            );
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

    if ("finalMatches" in data && data["finalMatches"] != null) {
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

            var matchNumber = i;
            var gameName;
            if (i == totalMatchNumber) {
                gameName = "Finale";
            } else if (i == totalMatchNumber - 1) {
                gameName = "Spiel um Platz 3";
            } else {
                gameName = "Halbfinalspiel " + matchNumber;
            }

            if (data["activeMatchNumber"] < -1) {
                if (
                    i + 1 == Math.abs(data["activeMatchNumber"]) &&
                    data["pauseMode"] == false
                ) {
                    generateFullSize(match, i, row, gameName);
                } else {
                    row.id = "section" + (i + 1) * -1; // Set the id of the row
                    var cellTime = row.insertCell(0);

                    if (
                        data["timeIntervalFM"] == null ||
                        data["timeIntervalFM"] == "0"
                    ) {
                        var matchTime = new Date(
                            finalMatchesTime.getTime() +
                                i * timeInterval * 60000
                        );
                    } else {
                        var matchTime = new Date(
                            finalMatchesTime.getTime() +
                                i * data["timeIntervalFM"] * 60000
                        );
                    }

                    cellTime.textContent = formatTime(matchTime);

                    var cellMatchNumber = row.insertCell(1);
                    cellMatchNumber.textContent = gameName;

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
                }
            }

            i++;
        });
    }
}

function generateFullSize(match, i, row, gameName = null) {
    // Create a bigger statistic entry in the table for the current match
    row.id = "section" + (i + 1); // Set the id of the row
    row.style.backgroundColor = "black";

    var dataNumber = 5;
    var colSpan = 6;

    var title = document.createElement("h2");
    if (gameName != null) {
        title.textContent = gameName;
        dataNumber = 4;
        colSpan = 5;
    } else if (match[4] == 1) {
        title.textContent = "Spiel " + (i + 1) + ": Gruppe A";
    } else if (match[4] == 2) {
        title.textContent = "Spiel " + (i + 1) + ": Gruppe B";
    }
    var fullSize = row.insertCell(0);
    fullSize.colSpan = colSpan;
    fullSize.className = "fullSize";

    title.className = "title";
    fullSize.appendChild(title);

    var contentDiv = document.createElement("div");
    contentDiv.className = "contentDiv";
    fullSize.appendChild(contentDiv);

    var team1Div = document.createElement("div");
    team1Div.className = "team1Div";
    contentDiv.appendChild(team1Div);

    var goalsDiv = document.createElement("div");
    goalsDiv.className = "goalsDiv";
    contentDiv.appendChild(goalsDiv);

    var team2Div = document.createElement("div");
    team2Div.className = "team2Div";
    contentDiv.appendChild(team2Div);

    var team1 = document.createElement("p");
    team1.textContent = match[0];
    team1.className = "team1";
    team1Div.appendChild(team1);

    var goals = document.createElement("p");
    goals.textContent = match[2] + " : " + match[3];
    goals.className = "goals";
    goalsDiv.appendChild(goals);

    var team2 = document.createElement("p");
    team2.textContent = match[1];
    team2.className = "team2";
    team2Div.appendChild(team2);

    if (match[dataNumber][2] == null || match[dataNumber][3] == null) {
        var tipping1 = document.createElement("p");
        tipping1.textContent = " ";
        tipping1.className = "tipping1";
        team1Div.appendChild(tipping1);

        var mustVote = document.createElement("p");
        mustVote.textContent = "Noch nicht getippt";
        mustVote.className = "style-loser";
        goalsDiv.appendChild(mustVote);

        var tipping2 = document.createElement("p");
        tipping2.textContent = " ";
        tipping2.className = "tipping2";
        team2Div.appendChild(tipping2);
    } else {
        var tipping1 = document.createElement("p");
        tipping1.textContent = match[dataNumber][2] + "%";
        tipping1.className = "tipping1";
        team1Div.appendChild(tipping1);

        var tippingGoals = document.createElement("p");
        tippingGoals.textContent = `${match[dataNumber][0]} : ${match[dataNumber][1]}`;
        tippingGoals.className = "tippingGoals";
        goalsDiv.appendChild(tippingGoals);

        var tipping2 = document.createElement("p");
        tipping2.textContent = match[dataNumber][3] + "%";
        tipping2.className = "tipping2";
        team2Div.appendChild(tipping2);

        if (match[dataNumber][2] > match[dataNumber][3]) {
            tipping1.className = "style-winner";
            tipping2.className = "style-loser";
        } else if (match[dataNumber][2] < match[dataNumber][3]) {
            tipping2.className = "style-winner";
            tipping1.className = "style-loser";
        } else {
            tipping1.className = "style-draw";
            tipping2.className = "style-draw";
        }
    }

    var description = document.createElement("p");
    description.textContent = "Tippspielauswertung";
    description.className = "description";
    fullSize.appendChild(description);
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
        KOMatchTable();
        finalMatchTable();
        setTimeout(function () {
            if (window.innerWidth > 1000) {
                window.location.hash = `section${data["activeMatchNumber"]}`;
            }
        }, 500);
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
window.location.hash = ``;
