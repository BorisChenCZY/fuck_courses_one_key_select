var express = require('express')
var bodyParser = require('body-parser')
var cheerio = require('cheerio')
var User = require('./Model/User')
var app = express()
var fs = require('fs')

var newUser = new User(req.body)

app.post('/class', function (req, res) {

  var newUser = new User(req.body)
  var loginUrl = 'https://cas.sustc.edu.cn/cas/login?service=http%3A%2F%2Fjwxt.sustc.edu.cn%2Fjsxsd%2Fxskb%2Fxskb_list.do'
  var target = {
    url: 'http://jwxt.sustc.edu.cn/jsxsd/xskb/xskb_list.do',
    method: 'GET',
    data: ''
  }
  newUser.login(loginUrl, target).then((response) => {
    var classTable = []
    var $ = cheerio.load(response)
    for (var i = 1; i <= 7; i++) {
      var reg = new RegExp('[A-Z0-9]{32}(\-' + i + '\-1){1}', 'g')
      var id = response.match(reg)
      for (var j = 0, k = 0; j < id.length; j++, k = k + 2) {

        var subject = ''
        var room = ''
        var classdetail = $('#' + id[k]).text()
        // console.log(classdetail)
        if (!classdetail) break
        if (classdetail !== ' ') {
          classdetails = classdetail.split('----------------------')
          var subject = [], room = [], week = [];
          for (let z = 0; z < classdetails.length; z++)
          {
            subject[z] = classdetails[z].match(/[\D]+(\d{1}习题课)?/)[0];
            room[z] = classdetails[z].match(/\){1}[^-]+/)[0];
            week[z] = classdetails[z].match(/\d.*?\)/)[0];
            // console.log(week[z])
          }

        }
        if (classTable[j] === undefined) classTable[j] = [];
        // if (subject.length== 0) {
        //     classTable[j].push({
        //     subject: '',
        //     room: '',
        //     week: '',
        //   })
        // }
        s = ''
        for (var z = 0; z < subject.length; z++){
          // console.log(week)
          tmp_week = week[z];
          tmp_week = tmp_week.substring(0, tmp_week.length - 1);
          if (tmp_week.match('单')) _week = '单周';
          else if (tmp_week.match('双')) _week = '双周';
          else _week = tmp_week.substring(0, tmp_week.length - 2) + '周';
          tmp_week = tmp_week.match(/.*?\(/)[0];
          tmp_week = tmp_week.substring(0, tmp_week.length - 1);
          var classinfo = {
            subject: subject[z],
            room: room[z].slice(1),
            week: tmp_week,
            day: i,
            classes: ([k + 1, k + 3]),
          }
          // console.log(classinfo)
          courses.push(classinfo)

          // if (courses[classinfo.subject]){
          //   this_courseinfo = courses[classinfo.subject];
          //   // console.log(this_courseinfo)
          //   this_courseinfo.classes = [this_courseinfo.classes[0], classinfo.classes[1]]
          // }else{
          //   courses[classinfo.subject] = classinfo;
          // }

          s += subject[z] + '\n\n' + room[z].slice(1) + '\n\n' + _week + '\n\n ------'
        }
        s = s.substring(0, s.length - 7)
        var classinfo = {
          text: s,
        }
        classTable[j].push(classinfo)
      }
    }
    res.send(classTable)
  })
})

app.post('/score', function (req, res) {
  var newUser = new User(req.body)
  var loginUrl = 'https://cas.sustc.edu.cn/cas/login?service=http%3A%2F%2Fjwxt.sustc.edu.cn%2Fjsxsd%2Fkscj%2Fcjcx_list'
  var target = {
    url: 'http://jwxt.sustc.edu.cn/jsxsd/kscj/cjcx_list',
    method: 'GET',
    data: ''
  }
  newUser.login(loginUrl, target).then((response) => {
    var $ = cheerio.load(response)
    var rawData = []
    var data = []
    $('#dataList tr td').each(function(i, item) {
      rawData[i] = $(this).text()
    })
    for (var i = 0; i < rawData.length; i = i + 11) {
      var scoreInfo = {
        term: rawData[i + 1],
        subject: rawData[i + 3],
        level: rawData[i + 4].match(/[A-Z]{1}(\+|\-)?/)[0],
        weight: rawData[i + 5]
      }
      data.push(scoreInfo)
    }
    res.send(data)
  })
})

app.post('/class/download', function(err, res){
  header = 'BEGIN:VCALENDAR\nVERSION:2.0\n'
  s = ''
  let time_interval = {}
  for (let i = 1; i <= 11; i++){
    time_interval[i] = `${i}0000`;
  }
  let start_date = 20170213;
  let actual_week = []
  // let courses_keys = Object.keys(courses)
  // console.log(1)
  // console.log(courses.length)
  // for (let i = 0; i < courses_keys.length; i++){
  for (let i = 0; i < courses.length; i++){
    // console.log(2)
    // course = courses[courses_keys[i]]
    course = courses[i];
    // console.log(courses)
    let tmp_intervals = course.week.split('-');
    var tmp_times = [];
    for (let i = 0; i < tmp_intervals.length; i++){
      let interval = tmp_intervals[i];
      // console.log('---:', interval.split(','))
      tmp_times = tmp_times.concat(interval.split(','))
    }
    // console.log(tmp_times)
    var this_times = tmp_times;

    for (var z =0; z < this_times.length; z++){
      let time = this_times[z];
      // console.log(this_times)
      s += `BEGIN:VEVENT\n`;
      let actual_date = start_date + (time - 1) * 7 + course.day - 1;
      s += `DTEND;TZID="China Standard Time":${actual_date}T${time_interval[course.classes[1]]}Z\n`
      s += `DTSTAMP;TZID="China Standard Time":${actual_date}T${time_interval[course.classes[0]]}Z\n`
      s += `DTSTART;TZID="China Standard Time":${actual_date}T${time_interval[course.classes[0]]}Z\n`
      s += `LOCATION:${course.room}\n`
      s += `SUMMARY:${course.subject}\n`
      s += `END:VEVENT\n`
    }


  }

  ender = 'END:VCALENDAR'
  console.log(s)
  fs.writeFile('./test.ics', header + s + ender, (err) => {
    if (err) throw err;
    console.log("it's saved");
  })
  res.send(null)
})

app.listen(3000)

var exit = function(req, res){

}
