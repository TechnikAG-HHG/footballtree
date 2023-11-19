var matchCount = 0; // Global variable to keep track of the total number of matches

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

    var matches1 = calculateMatchesForGroup(group1, "Group 1");
    var matches2 = calculateMatchesForGroup(group2, "Group 2");

    var matches = interleaveMatches(matches1, matches2);

    matches = matches.map(function(match) {
        matchCount++; // Increment the match count
        match.number = "Match " + (matchCount - 30);
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
            number: "Match " + matchCount,
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
        var headerCellGroup = headerRow.insertCell(0);
        headerCellGroup.textContent = "Spiele";
        headerCellGroup.className = "headerCell";
        headerCellGroup.colSpan = 4;

        table.appendChild(thead);
        table.appendChild(tbody);
        tablesContainer.appendChild(table);
    }

    // Add the new matches to the table
    matches.forEach(function(match) {
        var row = tbody.insertRow();

        var cellMatchNumber = row.insertCell(0);
        cellMatchNumber.textContent = match.number;

        var cellGroup = row.insertCell(1);
        cellGroup.textContent = match.group;

        var cellFirstTeam = row.insertCell(2);
        cellFirstTeam.textContent = match.teams[0];

        var cellSecondTeam = row.insertCell(3);
        cellSecondTeam.textContent = match.teams[1];
    });
}


function createTableForGroup(matches, tablesContainer) {
    var table = document.createElement("table");
    var thead = document.createElement("thead");
    var tbody = document.createElement("tbody");

    table.className = "tableGroup";

    var headerRow = thead.insertRow(0);
    var headerCellGroup = headerRow.insertCell(0);
    headerCellGroup.textContent = "Spiele";
    headerCellGroup.className = "headerCell";
    headerCellGroup.colSpan = 4;

    matches.forEach(function(match) {
        var row = tbody.insertRow();

        var cellMatchNumber = row.insertCell(0);
        cellMatchNumber.textContent = match.number;

        var cellGroup = row.insertCell(1);
        cellGroup.textContent = match.group;

        var cellFirstTeam = row.insertCell(2);
        cellFirstTeam.textContent = match.teams[0];

        var cellSecondTeam = row.insertCell(3);
        cellSecondTeam.textContent = match.teams[1];
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    tablesContainer.appendChild(table);
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

calculateMatches();
// call updateData() every 5 seconds
setInterval(updateData, 2000);