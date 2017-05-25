var superagent = require('superagent')
var cheerio = require('cheerio')

function User (obj) {
  this.loginMsg = obj
  this.cas_url = 'https://cas.sustc.edu.cn/cas/login'
}

User.prototype = {
  constructor: User,
  login: function (loginUrl, target) {
    loginUrl = loginUrl || this.cas_url
    target = target || { url: this.cas_url, method: 'GET', data: '' }
    return new Promise((resolve, reject) => {
      superagent.get(this.cas_url).end((err, res) => {
        if (!err) {
          var $ = cheerio.load(res.text)
          var loginMsg = this.loginMsg
          loginMsg.lt = $('[name=lt]').attr('value')
          loginMsg.execution = $('[name=execution]').attr('value')
          loginMsg._eventId = $('[name=_eventId]').attr('value')
          superagent.post(this.cas_url).type('form').send(loginMsg).end((err1, res1) => {
            var cookie = res1.headers['set-cookie']
            this.redirect(loginUrl, target, cookie, resolve)
          })
        } else {
          console.log(err)
        }
      })
    })
  },
  redirect: function (reurl, target, cookie, callback) {
    cookie = cookie || ''
    superagent.get(reurl).set('Cookie', cookie).redirects(1).end((err, res) => {
      if (res.headers.location) {
        if (res.headers['set-cookie']) {
          cookie = res.headers['set-cookie']
        }
        this.redirect(res.headers.location, target, cookie, callback)
      } else {
        if (target.method === 'GET') {
          superagent.get(target.url).set('Cookie', cookie).end((err, res) => {
            callback(res.text)
          })
        }
        if (target.method === 'POST') {
          superagent.post(target.url).set('Cookie', cookie).send(target.data).end((err, res) => {
            callback(res.text)
          })
        }
      }
    })
  }
}

module.exports = User
