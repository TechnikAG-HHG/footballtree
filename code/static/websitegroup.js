


function generateTables() {
    var tableCount = 2
    var teamCount = 12
    var entriesPerTable = teamCount / tableCount

    var tablesContainer = document.getElementById("tablesContainer");
    tablesContainer.innerHTML = '';

    for (var i = 1; i <= tableCount; i++) {
        var table = document.createElement("table");
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");

        table.className = "table" + i;

        var headerRow = thead.insertRow(0);
        var headerCellGroup = headerRow.insertCell(0);
        headerCellGroup.textContent = "Gruppe " + String.fromCharCode(64 + i);
        headerCellGroup.className = "headerCell";

        var headerCellSp = headerRow.insertCell(1);
        headerCellSp.textContent = "Sp";
        headerCellSp.className = "headerCell";

        var headerCellT = headerRow.insertCell(2);
        headerCellT.textContent = "T";
        headerCellT.className = "headerCell";

        var headerCellP = headerRow.insertCell(3);
        headerCellP.textContent = "P";
        headerCellP.className = "headerCell";

        for (var j = 1; j <= entriesPerTable; j++) {
            var row = tbody.insertRow(j - 1);
            var cellName = row.insertCell(0);
            cellName.textContent = j;
            cellName.className = "tableCell";
            cellName.className += " nameCell" + j;

            var cellSp = row.insertCell(1);
            cellSp.textContent = 0;
            cellSp.className = "tableCell";
            cellSp.className += " spCell" + j;

            var cellT = row.insertCell(2);
            cellT.textContent = ":";
            cellT.className = "tableCell";
            cellT.className += " tCell" + j;

            var cellP = row.insertCell(3);
            cellP.textContent = 0;
            cellP.className = "tableCell";
            cellP.className += " pCell" + j;
        }

        table.appendChild(thead);
        table.appendChild(tbody);
        tablesContainer.appendChild(table);
    }


    console.log('Initial data:', data);

    updateTables(data);
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

        // Example: Update the HTML to reflect the changes
        document.getElementById('output').innerHTML = 'Updated data: ' + JSON.stringify(data);
    })
    .catch(error => console.error('Error fetching data:', error));

    updateTables(data);
}


function updateTables(data) {
    var teams = data['Teams'];

    // update team names
    var i = 1;
    for (var team in teams) {
        var nameCell = table.getElementsByClassName("nameCell" + i);
        nameCell.textContent = team;
        i++;
    }
}

// generate tables on page load
generateTables();

// call updateData() every 5 seconds
setInterval(updateData, 5000);