function displayResult(elementId, data) {
    document.getElementById(elementId).innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}

// Search Videos
document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = document.getElementById('query').value;
    const response = await fetch(`/search/?query=${encodeURIComponent(query)}`);
    const data = await response.json();
    displayResult('search-results', data);
});

// Get Video Details
document.getElementById('video-details-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const videoId = document.getElementById('video-id').value;
    const response = await fetch(`/video/${videoId}/`);
    const data = await response.json();
    displayResult('video-details', data);
});

// Embed Video
document.getElementById('embed-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const videoId = document.getElementById('embed-video-id').value;
    const response = await fetch(`/embed/${videoId}/`);
    const data = await response.json();
    document.getElementById('embed-result').innerHTML = data.embed_code || '<p>Error embedding video.</p>';
});

// Get Channel Details
document.getElementById('channel-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const channelId = document.getElementById('channel-id').value;
    const response = await fetch(`/channel/${channelId}/`);
    const data = await response.json();
    displayResult('channel-details', data);
});

// Upload Video
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const videoPath = document.getElementById('video-url').value;
    const uploadStatus = document.getElementById('upload-status');
    const uploadButton = e.target.querySelector('button');

    try {
        uploadButton.disabled = true;
        uploadStatus.innerHTML = "<p style='color: blue;'>Uploading... Please wait.</p>";

        const response = await fetch('/upload/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_path: videoPath })
        });

        const data = await response.json();
        displayResult('upload-status', data);
    } catch (error) {
        console.error("Upload failed:", error);
        uploadStatus.innerHTML = "<p style='color: red;'>Upload failed. Please try again.</p>";
    } finally {
        uploadButton.disabled = false;
    }
});

// Edit Video Details
document.getElementById('edit-video-details-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const videoId = document.getElementById('edit-video-id').value;
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;
    const editStatus = document.getElementById('edit-video-details-status');
    const editButton = e.target.querySelector('button');

    try {
        editButton.disabled = true;
        editStatus.innerHTML = "<p style='color: blue;'>Updating details... Please wait.</p>";

        const response = await fetch('/edit-video-details/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ video_id: videoId, title: title, description: description })
        });

        const data = await response.json();
        displayResult('edit-video-details-status', data);
    } catch (error) {
        console.error("Update failed:", error);
        editStatus.innerHTML = "<p style='color: red;'>Update failed. Please try again.</p>";
    } finally {
        editButton.disabled = false;
    }
});
