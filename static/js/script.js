document.getElementById('join-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const location = document.getElementById('location').value;
    const destination = document.getElementById('destination').value;
    const contact = document.getElementById('contact').value;
    const data = { name, location, destination, contact };

    console.log("Sending data to submit:", data);
    fetch('http://127.0.0.1:5000/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log("Received from submit:", data);
        alert(data.message || data.error);
        if (data.message) {
            document.getElementById('join-form').reset();
            loadGroups();
        }
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('refresh-groups').addEventListener('click', loadGroups);

function loadGroups() {
    console.log("Loading groups");
    fetch('http://127.0.0.1:5000/groups')
    .then(response => response.json())
    .then(data => {
        console.log("Received groups data:", data);
        const groupsList = document.getElementById('groups-list');
        groupsList.innerHTML = '';
        for (const [dest, users] of Object.entries(data)) {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'group';
            groupDiv.innerHTML = `<h3>Destination: ${dest}</h3>`;
            users.forEach(user => {
                const userDiv = document.createElement('div');
                userDiv.className = 'user';
                userDiv.innerHTML = `<strong>${user.name}</strong> - Location: ${user.location} - Contact: ${user.contact}`;
                groupDiv.appendChild(userDiv);
            });
            groupsList.appendChild(groupDiv);
        }
        if (Object.keys(data).length === 0) {
            groupsList.innerHTML = '<p>No groups available yet.</p>';
        }
    })
    .catch(error => console.error('Error:', error));
}

// Load groups on page load
loadGroups();
