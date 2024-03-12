const express = require("express");
const { exec } = require("child_process");
const app = express();
const port = 5000;
const cors = require("cors");

app.use(express.json());
app.use(cors());

app.post("/run-script", (req, res) => {
  const pythonscript = 'Insurance_Cost.py';

  console.log("Starting Python script execution...");

  exec(`python ${pythonscript}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error}`);
      console.error(`Script output: ${stderr}`);
      res.status(500).send("Internal Server Error");
    } else {
      console.log(`Python script output: ${stdout}`);
      res.status(200).send("Script executed successfully");
    }
  });
});

app.post("/enquiry-script", (req, res) => {
  const pythonscript = 'enquiry.py'

  console.log("Starting Python script execution...");

  exec(`python ${pythonscript}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error}`);
      console.error(`Script output: ${stderr}`);
      res.status(500).send("Internal Server Error");
    } else {
      console.log(`Python script output: ${stdout}`);
      res.status(200).send("Script executed successfully");
    }
  });
});

app.post("/call-script", (req, res) => {
  const pythonscript = 'call_user.py'

  console.log("Starting Python script execution...");

  exec(`python ${pythonscript}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error}`);
      console.error(`Script output: ${stderr}`);
      res.status(500).send("Internal Server Error");
    } else {
      console.log(`Python script output: ${stdout}`);
      res.status(200).send("Script executed successfully");
    }
  });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});