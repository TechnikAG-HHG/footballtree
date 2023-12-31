var matchCount = 0; // Global variable to keep track of the total number of matches
var timeInterval = data["timeInterval"]; // Global variable to keep track of the time interval between matches

var startTime = new Date(); // Set the start time

startTime.setHours(0, 0, 0, 0);

function generateTableGroup(matches) {
    var tablesContainer = document.getElementById("tablesContainer");

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

    console.log(matches);
    // Add the new matches to the table
    var i = 0;
    matches.forEach((match) => {
        var row = tbody.insertRow();

        if (i == data["activeMatchNumber"]) {
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

function finalMatchTable() {
    if ("finalMatches" in data) {
        if (data["finalMatches"] == null) {
            return;
        }
        var tablesContainer = document.getElementById("tablesContainer");

        // If the table already exists, clear its contents
        var table = tablesContainer.querySelector(".tableFinalMatches");
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
        }

        var finalMatches = data["finalMatches"];
        if (finalMatches.length > Math.abs(data["activeMatchNumber"])) {
            if (finalMatches.length / 2 < Math.abs(data["activeMatchNumber"])) {
                var finalMatchesSliced = finalMatches;
            } else {
                var finalMatchesSliced = finalMatches.slice(0, 2);
            }
            while (finalMatchesSliced.length < finalMatches.length) {
                finalMatchesSliced.push(["???", "???", ["0", "0"]]);
            }
        }

        // Add the new matches to the table
        var i = 0;
        finalMatchesSliced.forEach((match) => {
            var row = tbody.insertRow();

            if (data["activeMatchNumber"] < 0) {
                if (i + 1 == Math.abs(data["activeMatchNumber"])) {
                    row.style.backgroundColor = "black";
                }
            }

            row.id = "section" + (i + 1) * -1; // Set the id of the row

            var cellTime = row.insertCell(0);
            var matchTime = new Date(
                finalMatchesTime.getTime() + i * timeInterval * 60000
            );
            cellTime.textContent = formatTime(matchTime);

            var cellMatchNumber = row.insertCell(1);
            var matchNumber = i + 1;
            if (i == data["finalMatches"].length - 1) {
                cellMatchNumber.textContent = "Finale";
            } else if (i == data["finalMatches"].length - 2) {
                cellMatchNumber.textContent = "Spiel um Platz 3";
            } else {
                cellMatchNumber.textContent = "Halbfinalspiel " + matchNumber;
            }

            var cellFirstTeam = row.insertCell(2);
            cellFirstTeam.textContent = match[0];

            var cellSecondTeam = row.insertCell(3);
            cellSecondTeam.textContent = match[1];

            var cellT = row.insertCell(4);
            cellT.textContent = match[2][0] + " : " + match[2][1];

            i++;
        });
    }
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

    setTimeout(function () {
        generateTableGroup(data["Matches"]);
        finalMatchTable();
    }, 500);
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
// call updateData() every 5 seconds
setInterval(updateData, 2000);
