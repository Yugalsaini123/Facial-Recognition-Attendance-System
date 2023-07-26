document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
  
    const formData = new FormData();
    formData.append('email', document.getElementById('email').value);
    formData.append('fullname', document.getElementById('fullname').value);
    formData.append('file', document.getElementById('file').files[0]);
  
    fetch('/upload', {
      method: 'POST',
      body: formData
    })
    .then(response => response.text())
    .then(data => {
      alert(data); // Display response from the server
      document.getElementById('email').value = '';
      document.getElementById('fullname').value = '';
      document.getElementById('file').value = '';
    })
    .catch(error => console.error('Error:', error));
  });
  