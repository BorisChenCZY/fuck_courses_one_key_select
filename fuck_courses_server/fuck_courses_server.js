var express = require('express')
var request = require('request')
var cheerio = require('cheerio')
var crypto = require('crypto')
var bodyParser = require('body-parser')

var app = express();
// var requests = superagent();
// var agent = requests.agent();

var sakai_url = 'http://sakai.sustc.edu.cn'
var CAS_base = 'https://cas.sustc.edu.cn/cas/login?service='

function cipher(algorithm, key, buf ,cb){
    var encrypted = "";
    var cip = crypto.createCipher(algorithm, key);
    encrypted += cip.update(buf, 'binary', 'hex');
    encrypted += cip.final('hex');
    cb(encrypted);
}

//解密
function decipher(algorithm, key, encrypted,cb){
    var decrypted = "";
    var decipher = crypto.createDecipher(algorithm, key);
    decrypted += decipher.update(encrypted, 'hex', 'binary');
    decrypted += decipher.final('binary');
    cb(decrypted);
}

cipher('aes-256-ctr', '11510237', 'BorisSpecialOffer', function(decrypted){
  console.log(decrypted)
})

app.get('/', function (req, res) {
  res.send('You accessed the server successfully!');
});
app.use(bodyParser())
app.post('/', function (req, res){
  var token = req.body.token
  var username = req.body['username']
  var permission = false
  cipher('aes-256-ctr', username, 'BorisSpecialOffer', function(decrypted){
    console.log(decrypted)
    console.log(token)
    if (decrypted == token)
      permission = true
      // res.send(true)
  })
  res.send(permission)
})

app.listen(3000, function(req, res){
  console.log('app is running at port 300')
})
