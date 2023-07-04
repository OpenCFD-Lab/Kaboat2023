const logger = require('./logger');
const multer = require('multer');
const fs = require('fs');
const uploadPath = __dirname+'/images'; // 업로드 디렉토리 지정
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        fs.mkdirSync(uploadPath, { recursive: true });
        cb(null, uploadPath);
    },
    filename: function (req, file, cb) {
        cb(null, file.originalname)
    }
})
const upload = multer({ storage: storage });
const bodyParser = require("body-parser");
const moment = require('moment');

// Express 및 app 기본 설정
const express = require('express');
app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 서버포트 지정
const port = process.env.PORT || 9000; // 서버 포트 지정

// 서버 리스닝(시작)
app.listen(port, function() {
    console.log("Server Listening on port " + port);
});

// Gps 정보 수신
app.post('/gps', (req, res) => {
    logger.info("[" + req.body.uname + "]" + "[GPS position] lon = " +req.body.longitude + ", lat = " + req.body.latitude);
    res.status(200).end();
});

// 이미지 정보 수신
app.post('/cam', upload.single('imagFile'), function(req,res){
    logger.info("[" + req.body.uname + "] '" + req.body.fileName + "' Uploaded");
    res.status(200).end();
});
