const express = require('express');
const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
const multer = require('multer');
const multerS3 = require('multer-s3');
const path = require('path');

const app = express();
const PORT = 3000;

// AWS S3 configuration
// Replace with your actual AWS credentials and bucket details
const AWS_ACCESS_KEY_ID = 'YOUR_AWS_ACCESS_KEY_ID ';
const AWS_SECRET_ACCESS_KEY = 'YOUR_AWS_SECRET_ACCESS_KEY ';
const AWS_REGION_NAME = 'ap-south-1';
const S3_BUCKET_NAME = 'students-imgs';

// Configure AWS SDK v3
const s3Client = new S3Client({
  credentials: {
    accessKeyId: AWS_ACCESS_KEY_ID,
    secretAccessKey: AWS_SECRET_ACCESS_KEY
  },
  region: AWS_REGION_NAME
});

// Function to specify the S3 object key
const s3Key = function (req, file, cb) {
  const fileName = Date.now().toString() + '-' + file.originalname;
  // The key will be 'index/fileName' inside the 'students-imgs' bucket
  cb(null, 'index/' + fileName);
};

// Configure multer middleware for file upload
const upload = multer({
  storage: multerS3({
    s3: s3Client,
    bucket: S3_BUCKET_NAME,
    metadata: function (req, file, cb) {
      cb(null, {
        'email': req.body.email,
        'fullname': req.body.fullname,
      });
    },
    key: s3Key // Use the custom key function
  }),
});

// Serve static files from the 'attendance_project' directory
const staticPath = path.join(__dirname, "public");
app.use(express.static(staticPath));

// Route handler for serving the index.html file
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Route to handle form submission
app.post('/upload', upload.single('file'), (req, res) => {
  const { email, fullname } = req.body;
  const fileLocation = req.file ? req.file.location : null;

  // Check if all required data is present
  if (!email || !fullname || !fileLocation) {
    return res.status(400).send('Missing required data.');
  }

  // Process the uploaded data (e.g., save to database, send response, etc.)
  // Your logic goes here...

  // Respond to the client
  res.send('File and data uploaded successfully!');
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});







































































