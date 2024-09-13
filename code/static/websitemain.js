// Function to handle button clicks and redirect
function redirectTo(path) {
    window.location.href = path;
}

async function updateData() {
    // Include the last data version in the request headers
    var headers = new Headers();
    headers.append('Last-Data-Update', data['LastUpdate']);

    await fetch('/update_data', {
        headers: headers,
    })
        .then((response) => response.json())
        .then((updatedData) => {
            console.log('Updated data:', updatedData);
            for (var key in data) {
                if (updatedData.hasOwnProperty(key)) {
                    data[key] = updatedData[key];
                }
            }
        })
        .catch((error) => console.error('Error fetching data:', error));

    document.title = data['websiteTitle'];
    document.getElementById('websiteTitle').textContent = data['websiteTitle'];

    if (data['bestScorerActive'] != true) {
        document.getElementById('bestScorerButton').style.display = 'none';
    } else {
        document.getElementById('bestScorerButton').style.display = 'block';
    }

    if (data['tippingActive'] == true) {
        document.getElementById('tippingButton').style.display = 'block';
    } else {
        document.getElementById('tippingButton').style.display = 'none';
    }
}

// Add click event listeners to the buttons
document.getElementById('planButton').addEventListener('click', function () {
    redirectTo('/plan');
});

document.getElementById('groupButton').addEventListener('click', function () {
    redirectTo('/group');
});

document.getElementById('treeButton').addEventListener('click', function () {
    redirectTo('/tree');
});

document
    .getElementById('bestScorerButton')
    .addEventListener('click', function () {
        redirectTo('/best_scorer');
    });

document.getElementById('tippingButton').addEventListener('click', function () {
    redirectTo('/tipping');
});

window.addEventListener('load', function () {
    document.title = data['websiteTitle'];
    document.getElementById('websiteTitle').textContent = data['websiteTitle'];
});

updateData();
setInterval(updateData, 10000);
