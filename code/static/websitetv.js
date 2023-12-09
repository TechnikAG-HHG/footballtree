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

getTeamData();
setInterval(getTeamData, 2000);
