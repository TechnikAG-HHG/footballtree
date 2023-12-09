function getTeamData() {
    var teamName1 = data["Matches"][data["activeMatchNumber"]][0];
    var teamName2 = data["Matches"][data["activeMatchNumber"]][1];

    var teamName1Element = document.getElementById("nextTeam1");
    var teamName2Element = document.getElementById("nextTeam2");

    teamName1Element.textContent = teamName1;
    teamName2Element.textContent = teamName2;

    console.log(teamName1, teamName2);

    var score1 = data["Matches"][data["activeMatchNumber"]][2];
    var score2 = data["Matches"][data["activeMatchNumber"]][3];

    var scoreElement = document.getElementById("scoreTeams");
    scoreElement.textContent = `${score1} : ${score2}`;
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

    setTimeout(function () {
        getTeamData();
    }, 500);
}

getTeamData();
setInterval(updateData, 2000);
