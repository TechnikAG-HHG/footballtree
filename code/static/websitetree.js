function drawTree() {
    var teamCount = 16;
    var boxes = teamCount;
    var boxheight = 20;
    var boxestodraw = 0;
    var textsdrawn = 0;
    var marginsubbox = 20;

    console.log("drawTree() called");


    // create the final box in the middle
    var boxfinal = document.createElement("div");
    // Set class for styling
    boxfinal.className = "drawn-box-final";
    boxfinal.style.height = `${boxheight}%`;
    document.getElementById("main-container").appendChild(boxfinal);

    var boxfinaltext = document.createElement("div");
    boxfinaltext.className = "team-name";
    boxfinaltext.className += ` text0`;
    boxfinal.appendChild(boxfinaltext);


    // calculate how many boxes to draw in each direction
    while (boxes > 2) {
        boxes = boxes / 2;
        boxestodraw++;
    }
    boxestodraw = boxestodraw + 2;


    // draw the boxes
    for (var i = 1; i < boxestodraw; i++) {
        //create the box1
        var box1 = document.createElement("div");
        box1.className = `box${i}`;
        box1.className += " drawn-box";
        box1.style.height = `${i * boxheight}%`;

        //create the box2
        var box2 = document.createElement("div");
        box2.className = `box${i}`;
        box2.className += " drawn-box";
        box2.style.height = `${i * boxheight}%`;
    
        // Append the boxes to the container
        document.getElementById("main-container").appendChild(box1);
        document.getElementById("main-container").prepend(box2);

        // create the subboxes
        var counter = i;
        var subboxestodraw = 2;
        while (counter > 0) {
            subboxestodraw = subboxestodraw * 2;
            counter--;
            console.log(subboxestodraw);
        }
        subboxestodraw = subboxestodraw / 4;

        for (var x = 0; x < subboxestodraw; x++) {
            var subboxmargintodraw =  marginsubbox
            
            var subbox1 = document.createElement("div");
            subbox1.className = `subbox${x}`;
            subbox1.className += " drawn-sub-box";
            subbox1.style.marginTop = `${subboxmargintodraw}px`;
            subbox1.style.marginBottom = `${subboxmargintodraw}px`;
            box1.appendChild(subbox1);
        
            var teamname1 = document.createElement("div");
            teamname1.className = "team-name";
            teamname1.className += ` text${(textsdrawn + 1) * 2}`;
            subbox1.appendChild(teamname1);
        
            var subbox2 = document.createElement("div");
            subbox2.className = `subbox${x}`;
            subbox2.className += " drawn-sub-box";
            subbox2.style.marginTop = `${subboxmargintodraw}px`;
            subbox2.style.marginBottom = `${subboxmargintodraw}px`;
            box2.appendChild(subbox2);
        
            var teamname2 = document.createElement("div");
            teamname2.className = "team-name";
            teamname2.className += ` text${(textsdrawn + 1) * 2 - 1}`;
            subbox2.appendChild(teamname2);

            textsdrawn++;
        }

        drawText(textsdrawn * 2);
    }
}

function drawText(textsdrawn) {
    while (textsdrawn > -1) {
        var textElement = document.querySelector(`.text${textsdrawn}`);
        if (textElement) {
            textElement.textContent = `${textsdrawn}`;
        }
        textsdrawn--;
    }
}  

drawTree();