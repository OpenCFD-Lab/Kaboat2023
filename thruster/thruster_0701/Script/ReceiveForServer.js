const logger = require('./logger');
const multer = require('multer');
const fs = require('fs');
const uploadPath = '/home/pi/OpenDEP/Receive/'; 
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

const port_Thruster = process.env.PORT || 9016;

app.listen(port_Thruster, function() {
    console.log("From Thruster :  " + port_Thruster + " Port is On");
});

app.post('/Thruster', upload_NewFile.single('ThrusterFile'), function(req, res){
    logger.info("[" + req.body.uname + "]" + req.body.fileName + ' Uploaded');
    res.status(200).end();
});

