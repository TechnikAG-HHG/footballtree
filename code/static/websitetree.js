function drawTree() {
    var teamCount = 16;
    var boxes = teamCount;
    var boxheight = 80;
    var boxestodraw = 0;
    var textsdrawn = 0;
    var marginsubbox = 500;

    console.log("drawTree() called");


    // create the final box in the middle
    var boxfinal = document.createElement("div");
    // Set class for styling
    boxfinal.className = "drawn-box-final";
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
        box1.style.height = `${boxheight}%`;

        //create the box2
        var box2 = document.createElement("div");
        box2.className = `box${i}`;
        box2.className += " drawn-box";
        box2.style.height = `${boxheight}%`;
    
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
            var subboxmargintodraw =  marginsubbox / Math.pow(2, i);
            
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


function setBoxFinalHeight() {
    var box1 = document.getElementsByClassName('subbox1')[0];
    if (box1) {
        var boxfinal = document.getElementsByClassName('drawn-box-final')[0];
        boxfinal.style.height = `${box1.offsetHeight / 4}%`;
    }
}


function drawLines() {
    // Create an SVG element
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.style.width = '100%';
    svg.style.height = '100%';
    svg.style.position = 'absolute';
    svg.style.top = '0';
    svg.style.left = '0';
    svg.style.zIndex = '1';
    document.getElementById("main-container").appendChild(svg);

    // Get all the boxes
    var boxes = Array.from(document.getElementsByClassName('drawn-box'));

    // Find the boxfinal
    var boxfinal = document.getElementsByClassName('drawn-box-final')[0];

    // If boxfinal is not in boxes, use the middle box
    var middleIndex = boxes.indexOf(boxfinal);
    if (middleIndex === -1) {
        middleIndex = Math.floor(boxes.length / 2);
    }

    // Draw lines to the left
    for (var i = middleIndex - 1; i >= 0; i--) {
        if (boxes[i + 1]) {
            drawLinesBetweenBoxes(boxes[i + 1], boxes[i], svg);
        }
    }

    // Draw lines to the right
    for (var i = middleIndex; i < boxes.length - 1; i++) {
        if (boxes[i + 1]) {
            drawLinesBetweenBoxes(boxes[i], boxes[i + 1], svg);
        }
    }
}

function drawLinesBetweenBoxes(box, nextBox, svg) {
    // Get the subboxes of the box and the next box
    var subboxes = box.getElementsByClassName('drawn-sub-box');
    var nextSubboxes = nextBox.getElementsByClassName('drawn-sub-box');

    // For each subbox
    for (var j = 0; j < subboxes.length; j++) {
        var subbox = subboxes[j];

        // Calculate the coordinates of the start point of the line
        var x1 = subbox.offsetLeft + subbox.offsetWidth / 2;
        var y1 = subbox.offsetTop + subbox.offsetHeight / 2;

        // For each of the two subboxes directly below the current subbox
        for (var k = 2*j; k < 2*j + 2 && k < nextSubboxes.length; k++) {
            var nextSubbox = nextSubboxes[k];

            // Calculate the coordinates of the end point of the line
            var x2 = nextSubbox.offsetLeft + nextSubbox.offsetWidth / 2;
            var y2 = nextSubbox.offsetTop + nextSubbox.offsetHeight / 2;

            // Create an SVG line element for the horizontal line
            var line1 = document.createElementNS("http://www.w3.org/2000/svg", 'line');
            line1.setAttribute('x1', x1);
            line1.setAttribute('y1', y1);
            line1.setAttribute('x2', x1);
            line1.setAttribute('y2', y2);
            line1.setAttribute('stroke', '#49ba67');
            line1.setAttribute('stroke-width', '5');

            // Create an SVG line element for the vertical line
            var line2 = document.createElementNS("http://www.w3.org/2000/svg", 'line');
            line2.setAttribute('x1', x1);
            line2.setAttribute('y1', y2);
            line2.setAttribute('x2', x2);
            line2.setAttribute('y2', y2);
            line2.setAttribute('stroke', '#49ba67');
            line2.setAttribute('stroke-width', '5');

            // Append the lines to the SVG element
            svg.appendChild(line1);
            svg.appendChild(line2);

            subbox.style.backgroundColor = '#1a1a1a';
        }
    }
}


drawTree();

// Use setTimeout to delay the execution of setBoxFinalHeight
window.setTimeout(setBoxFinalHeight, 0);

drawLines();