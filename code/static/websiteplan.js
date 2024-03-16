var matchCount = 0; // Global variable to keep track of the total number of matches
var timeInterval = data["timeInterval"]; // Global variable to keep track of the time interval between matches

var startTime = new Date(); // Set the start time
var finalMatchesTime = new Date(); // Set the final matches time
var KOMatchesTime = new Date(); // Set the K.O. matches time

var pauseCount = 4; // Global variable to keep track of the total number of pauses
var pauseTimes = []; // Global array to keep track of the pause times
var positions = []; // Global array to keep track of the positions of the pause times

startTime.setHours(0, 0, 0, 0);

var intervalActivated = false;

function generateTableGroup(matches) {
    console.log("Generating table group");
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

        if (i == data["activeMatchNumber"] && data["pauseMode"] == -1) {
            generateFullSize(match, data["activeMatchNumber"], i, row);
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
                (data["activeMatchNumber"] != -1 &&
                    data["activeMatchNumber"] > i) ||
                (data["activeMatchNumber"] < 0 &&
                    data["activeMatchNumber"] != -1)
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

function generatePauseTime(time, pos, startTime, pauseID) {
    if (time == 0 || time == null || time == "0") {
        let pauseTimeDiv = document.getElementById(`pauseTime${pauseID}`);
        if (pauseTimeDiv) {
            pauseTimeDiv.remove();
            pauseTimes[pauseID] = null;
            positions[pauseID] = null;
        }
    }

    positions[pauseID] = pos;

    stopTime = new Date(startTime.getTime() + time * 60000);
    if (pos > -1) {
        var colSpan = 6;
    } else {
        var colSpan = 5;
    }

    // get the element with the id section-position
    let elementBeforePause = document.getElementById(`section${pos}`);

    if (elementBeforePause == null) {
        return startTime;
    }

    let pauseTimeText = document.getElementById(`pauseTimeText${pauseID}`);
    let pauseTimeElement = document.getElementById(`pauseTimeProgress${pauseID}`);
    let pauseTimeStart = document.getElementById(`pauseTimeStart${pauseID}`);
    let pauseTimeEnd = document.getElementById(`pauseTimeEnd${pauseID}`);

    if (pauseTimeElement) {
        pauseTimeText.textContent = `Pause ${time} Minuten`;
        pauseTimeStart.textContent = `${formatTime(startTime)}`;
        pauseTimeEnd.textContent = `${formatTime(stopTime)}`;

        pauseTimes[pauseID] = startTime;
    } else {
        pauseTimes[pauseID] = startTime;

        let pauseTimeDiv = document.createElement("div");
        pauseTimeDiv.className = "pauseTime";

        pauseTimeElement = document.createElement("progress");
        pauseTimeElement.id = `pauseTimeProgress${pauseID}`;
        pauseTimeElement.className = "pauseTimeProgress";
        pauseTimeElement.max = time * 60;
        pauseTimeElement.value = 0;

        pauseTimeText = document.createElement("p");
        pauseTimeText.textContent = `Pause ${time} Minuten`;
        pauseTimeText.id = `pauseTimeText${pauseID}`;
        pauseTimeText.className = "pauseTimeText";

        pauseTimeStart = document.createElement("p");
        pauseTimeStart.textContent = `${formatTime(startTime)}`;
        pauseTimeStart.id = `pauseTimeStart${pauseID}`;
        pauseTimeStart.className = "pauseTimeStart";

        pauseTimeEnd = document.createElement("p");
        pauseTimeEnd.textContent = `${formatTime(stopTime)}`;
        pauseTimeEnd.id = `pauseTimeEnd${pauseID}`;
        pauseTimeEnd.className = "pauseTimeEnd";

        pauseTimeDiv.appendChild(pauseTimeStart);
        pauseTimeDiv.appendChild(pauseTimeText);
        pauseTimeDiv.appendChild(pauseTimeEnd);
        pauseTimeDiv.appendChild(pauseTimeElement);

        if (elementBeforePause.nextSibling) {
            let pauseTimeTr = document.createElement("tr");
            let pauseTimeTd = document.createElement("td");
            pauseTimeTd.colSpan = colSpan;
            pauseTimeTd.appendChild(pauseTimeDiv);
            pauseTimeTr.appendChild(pauseTimeTd);

            elementBeforePause.parentNode.insertBefore(
                pauseTimeTr,
                elementBeforePause.nextSibling
            );
        } else {
            document.getElementById('tablesContainer').appendChild(pauseTimeDiv);
        }
    }

    return stopTime;
}

function checkForPauseUpdate() {
    console.log("Checking for pause update");
    for (var i = 0; i < pauseCount; i++) {
        var pauseTimeElement = document.getElementById(`pauseTimeProgress${i}`);

        if (pauseTimeElement) {
            if (i == data["pauseMode"]) {
                console.log("Pause mode activated");
                intervalActivated = true;
            } else {
                console.log("Pause mode not activated");
                if (i < data["pauseMode"]) {
                    pauseTimeElement.value = 999999999;
                } else if (data["activeMatchNumber"] < -1 && data["activeMatchNumber"] > -100) {
                    if (positions[i] > data["activeMatchNumber"] || positions[i] < -99) {
                        pauseTimeElement.value = 999999999;
                    } else {
                        pauseTimeElement.value = 0;
                    }
                } else if (data["activeMatchNumber"] < -99) {
                    if (positions[i] > data["activeMatchNumber"] ) {
                        pauseTimeElement.value = 999999999;
                    } else {
                        pauseTimeElement.value = 0;
                    }
                } else if (positions[i] < data["activeMatchNumber"] || data["activeMatchNumber"] < -1) {
                    pauseTimeElement.value = 999999999;
                } else {
                    pauseTimeElement.value = 0;
                }
            }
        }
    }
}

function updatePauseTime() {
    if (intervalActivated == true) {
        // update the progress bar with the current time and the finalmatchtime
        let pauseTimeElement = document.getElementById(`pauseTimeProgress${data["pauseMode"]}`);
        console.log(pauseTimeElement);
        if (pauseTimeElement) {
            let currentTime = new Date();
            let timeDifference = currentTime - pauseTimes[data["pauseMode"]];
            let timeDifferenceInSeconds = timeDifference / 1000;
            pauseTimeElement.value = timeDifferenceInSeconds;
        }
    }
}

function KOMatchTable() {
    console.log("Generating K.O. match table");
    if (
        data["KOMatches"] == null ||
        data["KOMatches"] == "null" ||
        data["KOMatches"] == "" ||
        data["KOMatches"] == "[]" ||
        data["KOMatches"] === 0
    ) {
        console.log("No matches found");
        finalMatchesTime = new Date(KOMatchesTime.getTime());
        return; // Add return statement here
    }

    if ("KOMatches" in data && data["KOMatches"] != null) {
        if (data["pauseBeforeKOMatches"] != null && data["pauseBeforeKOMatches"] != "0") {
            var requestedtime = parseInt(data["pauseBeforeKOMatches"]);
            KOMatchesTime = generatePauseTime(requestedtime, 12, KOMatchesTime, 0);
        }

        var tablesContainer = document.getElementById("tablesContainer");

        var table = tablesContainer.querySelector(".tableKOMatches");
        var tbody;

        if (table) {
            tbody = table.querySelector("tbody");
            while (tbody.firstChild) {
                tbody.removeChild(tbody.firstChild);
            }
        } else {
            table = document.createElement("table");
            var thead = document.createElement("thead");
            tbody = document.createElement("tbody");

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
        }

        var KOMatches = data["KOMatches"];
        if (KOMatches != null) {
            var i = 100;
            var y = 0;
            KOMatches.forEach((match) => {
                var row = tbody.insertRow();

                if (data["activeMatchNumber"] < -1) {
                    if (
                        i == Math.abs(data["activeMatchNumber"]) &&
                        data["pauseMode"] == -1
                    ) {
                        generateFullSize(
                            match,
                            data["activeMatchNumber"],
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
                    y * data["timeIntervalFM"] * 60000
            );
        }
    }
}

function finalMatchTable() {
    console.log("Generating final match table");
    if (
        data["Matches"] == null ||
        data["Matches"] == "null" ||
        data["Matches"] == "" ||
        data["Matches"] == "[]" ||
        data["Matches"] === 0
    ) {
        console.log("No matches found");
        return;
    }

    if ("finalMatches" in data && data["finalMatches"] != null) {
        if (data["pauseBeforeFM"] != null && data["pauseBeforeFM"] != "0") {
            var requestedtime = parseInt(data["pauseBeforeFM"]);
            if (data["KOMatches"] != null) {
                finalMatchesTime = new Date (generatePauseTime(requestedtime, -103, finalMatchesTime, 1));
            } else {
                finalMatchesTime = new Date(generatePauseTime(requestedtime, 12, finalMatchesTime, 1));
            }
            finalMatchesTime = new Date(finalMatchesTime.getTime() - data["timeIntervalFM"] * 60000);
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
                finalMatchesSliced.push(["???", "???", "0", "0", [null, null, null, null]]);
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
                    finalMatchesSliced.push(["???", "???", "0", "0", [null, null, null, null]]);
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
            console.log("Match:", match);

            finalMatchesTime = new Date(
                finalMatchesTime.getTime() + data["timeIntervalFM"] * 60000);

            var matchNumber = i;
            var gameName;
            if (i == totalMatchNumber) {
                gameName = "Finale";
                if (data["halfTimePause"] != null && data["halfTimePause"] != "0") {
                    finalMatchesTime = new Date(generatePauseTime(parseInt(data["halfTimePause"]), -4, finalMatchesTime, 3
                    ));
                }
            } else if (i == totalMatchNumber - 1) {
                console.log("Spiel um Platz 3");
                gameName = "Spiel um Platz 3";
                if (data["pauseBeforeTheFinalMatch"] != null && data["pauseBeforeTheFinalMatch"] != "0") {
                    finalMatchesTime = new Date(generatePauseTime(parseInt(data["pauseBeforeTheFinalMatch"]), -3, finalMatchesTime, 2));
                }
            } else {
                gameName = "Halbfinalspiel " + matchNumber;
            }

            if (data["activeMatchNumber"] < -1) {
                if (
                    i + 1 == Math.abs(data["activeMatchNumber"]) &&
                    data["pauseMode"] == -1
                ) {
                    generateFullSize(match, data["activeMatchNumber"], i, row, gameName);
                } else {
                    row.id = "section" + (i + 1) * -1; // Set the id of the row
                    var cellTime = row.insertCell(0);

                    cellTime.textContent = formatTime(finalMatchesTime);

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
        });
    }
}

function generateFullSize(match, matchID, i, row, gameName = null) {
    // Create a bigger statistic entry in the table for the current match
    row.id = "section" + matchID; // Set the id of the row
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

    await generateTableGroup(data["Matches"]);
    await KOMatchTable();
    await finalMatchTable();
    await checkForPauseUpdate();
    await new Promise(resolve => setTimeout(resolve, 500));
    if (window.innerWidth > 1000) {
        window.location.hash = `section${data["activeMatchNumber"]}`;
    }
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
setInterval(updatePauseTime, 10);
window.location.hash = ``;
