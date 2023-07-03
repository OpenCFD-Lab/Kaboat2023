const logger = require('./logger');
const path = require('path')
const execSync = require('child_process').execSync;
const multer = require('multer');
const fs = require('fs');
//const uploadPath = __dirname+'/LidarSimulation';
const uploadPath ='/home/opencfd/OpenDEP/Receive/';
const storage_NewFile = multer.diskStorage({
    destination: function (req, file, cb) {
        const Dir = uploadPath +"/" + req.body.uname;
        fs.exists(Dir, exist => {
            if (!exist) {
                return fs.mkdir(Dir, error => cb(error, Dir))
            }
            return cb(null, Dir)
        })
    },
    filename: function (req, file, cb) {
        //cb(null, new Date().toFormat('YYYY-MM-DD HH24:MI:SS')+' '+file.originalname)
        cb(null, file.originalname)
    }
})

const upload_NewFile = multer({ storage: storage_NewFile });
const bodyParser = require("body-parser");
const moment = require('moment');

const express = require('express');
app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const port_Lidar = process.env.PORT || 9012; // Set 
const port_GPS = process.env.PORT || 9013; // Set
const port_Gyro = process.env.PORT || 9014; // Set 
const port_Thruster = process.env.PORT || 9026; // Set 
const port_Cam = process.env.PORT || 9004;

app.listen(port_Lidar, function() {
    console.log("From Lidar : " + port_Lidar + " Port is On");
});

app.listen(port_GPS, function() {
    console.log("From GPS : " + port_GPS + " Port is On");
});

app.listen(port_Gyro, function() {
    console.log("From Gyro : " + port_Gyro + " Port is On");
});

app.listen(port_Thruster, function() {
    console.log("From Thruster : " + port_Thruster + " Port is On");
});

app.listen(port_Cam, function() {
    console.log("From Cam : " + port_Cam + " Port is On");
});

app.post('/Lidar', upload_NewFile.single('lidarFile'), function(req,res){
    logger.info('[' + req.body.uname + '] ' + req.body.fileName + ' Uploaded');
    res.status(200).end();
});


app.post('/GPS', upload_NewFile.single('GPSFile'), function(req,res){
    logger.info('[' + req.body.uname + '] ' + req.body.fileName + ' Uploaded');
    res.status(200).end();
});


app.post('/Gyro', upload_NewFile.single('GyroFile'), function(req,res){
    logger.info('[' + req.body.uname + '] ' + req.body.fileName + ' Uploaded');
    res.status(200).end();
});

app.post('/Thruster', upload_NewFile.single('ThrusterFile'), function(req,res){
    logger.info('[' + req.body.uname + '] ' + req.body.fileName + ' Uploaded');
    res.status(200).end();
});

app.post('/Cam', upload_NewFile.single('CamFile'), function(req,res){
    logger.info('[' + req.body.uname + '] ' + req.body.fileName + ' Uploaded');
    res.status(200).end();
});
