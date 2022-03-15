/* globals Quasar, Vue, _, VueQrcode, windowMixin, LNbits, LOCALE */

Vue.component(VueQrcode.name, VueQrcode)

const pica = window.pica()

var locationPath = [
  window.location.protocol,
  '//',
  window.location.host,
  window.location.pathname
].join('')

var mapGameLink = obj => {
  obj._data = _.clone(obj)
  console.log(obj._data)
  obj.print_url = [locationPath, 'print/', obj.id].join('')
  obj.pay_url = [locationPath, obj.id].join('')
  console.log(obj.print_url)
  return obj
}

new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      eightball: {
      },
      qrCodeDialog: {
        show: false,
        data: null
      },
      gameLinks: [],
      gameLinksTable: {
        pagination: {
          rowsPerPage: 10
        }
      },
      wordlist: ["It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes - definitely",
        "You may rely on it",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",
        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful"],
      gameDialog: {
        show: false,
        data: {
          wordlist:"",
          name: "Magic 8-ball",
          description: "Pay 10 sats for magic 8-ball wisdom",
          price: 10
        },
        units: ['sat']
      }
    }
  },

  methods: {
    openNewDialog() {
      this.gameDialog.show = true
    },
    loadgames() {
      LNbits.api
        .request(
          'GET',
          '/eightball/api/v1/eightball',
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          //console.log(response.data)
          this.gameLinks = response.data.map(mapGameLink)
        })
        .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
    },
    sendGame() {
      
      if (!this.gameDialog.data.wallet){
        this.gameDialog.data.wallet = this.g.user.wallets[0].id
      }
 
          LNbits.api.request(
            'POST',
            '/eightball/api/v1/eightball/games',
            this.g.user.wallets[0].adminkey,
            this.gameDialog.data
          )
          .then(response => {
            console.log(mapGameLink(response.data))
            this.gameLinks = response.data.map(mapGameLink)
            this.gameDialog.show = false
            this.$q.notify({
              message: `Game '${this.gameDialog.data.name}' added.`,
              timeout: 700
            })
         })
         .catch(err => {
          LNbits.utils.notifyApiError(err)
        })
      this.gameDialog.show = false
    },
    deleteGame(gameId) {
      LNbits.utils
        .confirmDialog('Are you sure you want to delete this game?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              '/eightball/api/v1/eightball/games/' + gameId,
              this.g.user.wallets[0].adminkey
            )
            .then(response => {
              this.$q.notify({
                message: `Game deleted.`,
                timeout: 700
              })
              this.gameLinks = response.data.map(mapGameLink)
            })
            .catch(err => {
              LNbits.utils.notifyApiError(err)
            })
        })
    }
  },
  created() {
    this.gameDialog.data.wordlist = this.wordlist.join("\n")
    this.selectedWallet = this.g.user.wallets[0]
    this.loadgames()
  }
})
