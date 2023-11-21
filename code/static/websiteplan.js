var matchCount = 0; // Global variable to keep track of the total number of matches
var timeInterval = 8;

var startTime = new Date(); // Set the start time
startTime.setHours(10, 0, 0, 0); // Set the start time to 10:00

function calculateMatches() {
    matchCount = 0; // Reset matchCount to 0

    var teams = data.Teams.slice(); // Create a copy of the teams array
    // If the number of teams is odd, add a "dummy" team
    if (teams.length % 2 !== 0) {
        teams.push("dummy");
    }

    teams.sort((a, b) => a - b);

    var midpoint = Math.ceil(teams.length / 2);
    var group1 = teams.slice(0, midpoint);
    var group2 = teams.slice(midpoint);

    var matches1 = calculateMatchesForGroup(group1, "Gruppe 1");
    var matches2 = calculateMatchesForGroup(group2, "Gruppe 2");

    var matches = interleaveMatches(matches1, matches2);

    matchCount = 0; // Reset matchCount to 0

    matches = matches.map(function(match) {
        matchCount++; // Increment the match count
        match.number = "Spiel " + (matchCount);
        return match;
    });
  
    generateTableGroup(matches);
}


function calculateMatchesForGroup(teams, groupName) {
    var rounds = [];

    for (var round = 0; round < teams.length - 1; round++) {
        rounds[round] = [];
        for (var match = 0; match < teams.length / 2; match++) {
            var team1 = teams[match];
            var team2 = teams[teams.length - 1 - match];
            rounds[round][match] = [team1, team2];
        }
        // Rotate the teams for the next round
        teams.splice(1, 0, teams.pop());
    }

    // Remove matches with the "dummy" team
    if (teams.includes("dummy")) {
        rounds = rounds.map(function(round) {
            return round.filter(function(match) {
                return !match.includes("dummy");
            });
        });
    }

    var matches = rounds.reduce(function(allMatches, round) {
        return allMatches.concat(round);
    }, []);

    matches = matches.map(function(match) {
        matchCount++; // Increment the match count
        return {
            number: "Spiel " + matchCount,
            teams: match,
            group: groupName
        };
    });

    return matches;
}


function interleaveMatches(matches1, matches2) {
    var matches = [];
    var i = 0, j = 0;
    while (i < matches1.length || j < matches2.length) {
        if (i < matches1.length) {
            matches.push(matches1[i++]);
        }
        if (j < matches2.length) {
            matches.push(matches2[j++]);
        }
    }
    return matches;
}


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

    // Add the new matches to the table
    matches.forEach(function(match) {
        var row = tbody.insertRow();

        var cellTime = row.insertCell(0);
        var matchNumber = parseInt(match.number.split(" ")[1]);
        var matchTime = new Date(startTime.getTime() + matchNumber * timeInterval * 60000);
        cellTime.textContent = formatTime(matchTime);

        console.log(match.number);

        var cellMatchNumber = row.insertCell(1);
        cellMatchNumber.textContent = match.number;

        var cellGroup = row.insertCell(2);
        cellGroup.textContent = match.group;

        var cellFirstTeam = row.insertCell(3);
        cellFirstTeam.textContent = match.teams[0];

        var cellSecondTeam = row.insertCell(4);
        cellSecondTeam.textContent = match.teams[1];

        var cellT = row.insertCell(5);
        cellT.textContent = ":";
    });
}


function updateData() {
    // Include the last data version in the request headers
    var headers = new Headers();
    headers.append('Last-Data-Update', data['LastUpdate']);

    fetch('/update_data', {
        headers: headers
    })
    .then(response => response.json())
    .then(updatedData => {
        console.log('Updated data:', updatedData);

        // Update variables in JavaScript
        for (var key in updatedData) {
            if (updatedData.hasOwnProperty(key)) {
                data[key] = updatedData[key];
            }
        }
    })
    .catch(error => console.error('Error fetching data:', error));

    setTimeout(function() {
        calculateMatches();
    }, 500);
}


function formatTime(date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    return (hours < 10 ? '0' : '') + hours + ':' + (minutes < 10 ? '0' : '') + minutes + ' Uhr';
}


calculateMatches();
// call updateData() every 5 seconds
setInterval(updateData, 2000);