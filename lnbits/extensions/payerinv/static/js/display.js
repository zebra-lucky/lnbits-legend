Vue.component(VueQrcode.name, VueQrcode)

new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data: function () {
    return {
      LNBITS_DENOMINATION: LNBITS_DENOMINATION,
      captchaGuess: '',
      captchaB64: '',
      captchaUuid: '',
      invDlg: {
        show: false,
        invoice: {}
      }
    }
  },
  mounted() {
    this.captchaB64 = captchaB64
    this.captchaUuid = captchaUuid
  },
  methods: {
    createInvoice() {
      if (!this.captchaGuess) {
        this.$q.notify({
          timeout: 5000,
          type: 'warning',
          message: 'Please enter captcha guess'
        })
        return
      }
      LNbits.api
        .request('POST', '/payerinv/api/v1/captcha/' + this.captchaUuid +
                 '?captcha_guess=' + this.captchaGuess)
        .then(response => {
          data = response.data
          if (!data.correct) {
            error = data.error
            if (error) {
                err_msg = 'Captcha guess error: ' + error + '!'
            } else {
                err_msg = 'Wrong captcha guess!'
            }
            throw err_msg
          } else {
            LNbits.utils
            .confirmDialog('Are you sure you want to create lightning invoice?')
            .onOk(() => {
              LNbits.api
                .request('POST', '/payerinv/api/v1/links/' + linkId + '/inv' +
                         '?captcha_uuid=' + this.captchaUuid +
                         '&captcha_guess=' + this.captchaGuess)
                .then(response => {
                  this.showInvoice(response)
                })
                .catch(err => {
                  LNbits.utils.notifyApiError(err)
                })
            })
          }
        })
        .catch((err) => {
          if (err.status) {
            LNbits.utils.notifyApiError(err)
          } else {
            this.$q.notify({
              timeout: 5000,
              type: 'warning',
              message: err
            })
          }
        })
    },
    generateCaptcha() {
      LNbits.api
        .request('POST', '/payerinv/api/v1/captcha/')
        .then(response => {
          data = response.data
          this.captchaUuid = data.captchaUuid
          this.captchaB64 = data.captchaB64
        })
        .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
    },
    showInvoice(res) {
        inv = res.data.invoice
        inv.date = Quasar.utils.date.formatDate(
            new Date(inv.time * 1000), 'YYYY-MM-DD HH:mm'
        )
        inv.expireDate = Quasar.utils.date.formatDate(
          (inv.time + inv.expiry) * 1000, 'YYYY-MM-DD HH:mm'
        )
        this.invDlg.invoice = inv
        this.invDlg.show = true
    }
  }
})
