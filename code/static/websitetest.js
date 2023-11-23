function calculateMatches(teams) {
    // If the number of teams is odd, add a "dummy" team
    if (teams.length % 2 !== 0) {
        teams.push("dummy");
    }

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
        rounds = rounds.map(function (round) {
            return round.filter(function (match) {
                return !match.includes("dummy");
            });
        });
    }

    return rounds;
}

var teams = [
    "Team1",
    "Team2",
    "Team3",
    "Team4",
    "Team5",
    "Team6",
    "Team7",
    "Team8",
    "Team9",
    "Team10",
    "Team11",
    "Team12",
];
var matches = calculateMatches(teams);
console.log(matches);
