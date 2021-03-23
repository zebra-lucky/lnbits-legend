/* global Vue, VueQrcode, _, Quasar, LOCALE, windowMixin, LNbits */

Vue.component(VueQrcode.name, VueQrcode)

var locationPath = [
  window.location.protocol,
  '//',
  window.location.host,
  window.location.pathname
].join('')

var mapscramblesgame = function (obj) {
  obj._data = _.clone(obj)
  obj.date = Quasar.utils.date.formatDate(
    new Date(obj.time * 1000),
    'YYYY-MM-DD HH:mm'
  )
  obj.tleft = obj.top_left
  obj.bright = obj.bottom_right
  obj.scrambles_url = [locationPath, obj.id].join('')
  return obj
}

new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data: function () {
    return {
      checker: null,
      scramblesgames: [],
      scramblesgamesTable: {
        columns: [
          {name: 'id', align: 'left', label: 'ID', field: 'id'},
          {name: 'title', align: 'left', label: 'Title', field: 'title'},
          {name: 'topleft', align: 'right', label: 'Top left words', field: 'tleft'},
          {name: 'bottomright', align: 'right', label: 'Bottom right words', field: 'bright'}
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      formDialog: {
        show: false,
        data: {
          is_unique: false
        }
      },
      qrCodeDialog: {
        show: false,
        data: null
      }
    }
  },
  computed: {
    sortedscramblesgames: function () {
      return this.scramblesgames.sort(function (a, b) {
        return
      })
    }
  },
  methods: {
    getscramblesgames: function () {
      var self = this

      LNbits.api
        .request(
          'GET',
          '/scrambles/api/v1/games?all_wallets',
          this.g.user.wallets[0].inkey
        )
        .then(function (response) {
          self.scramblesgames = response.data.map(function (obj) {
            return mapscramblesgame(obj)
          })
        })
        .catch(function (error) {
          clearInterval(self.checker)
          LNbits.utils.notifyApiError(error)
        })
    },
    closeFormDialog: function () {
      this.formDialog.data = {
        is_unique: false
      }
    },
    openQrCodeDialog: function (gameId) {
      var game = _.findWhere(this.scramblesgames, {id: gameId})

      this.qrCodeDialog.data = _.clone(game)
      console.log(this.qrCodeDialog.data)
      this.qrCodeDialog.data.url =
        window.location.protocol + '//' + window.location.host
      this.qrCodeDialog.show = true
    },
    openUpdateDialog: function (gameId) {
      var game = _.findWhere(this.scramblesgames, {id: gameId})
      this.formDialog.data = _.clone(game._data)
      this.formDialog.show = true
    },
    sendFormData: function () {
      var wallet = _.findWhere(this.g.user.wallets, {
        id: this.formDialog.data.wallet
      })
      var data = _.omit(this.formDialog.data, 'wallet')
      if (data.id) {
        this.updatescramblesgame(wallet, data)
      } else {
        this.createscramblesgame(wallet, data)
      }
    },
    simplesendFormData: function () {
      var wallet = _.findWhere(this.g.user.wallets, {
        id: this.simpleformDialog.data.wallet
      })
      var data = _.omit(this.simpleformDialog.data, 'wallet')

      data.title = 'game'

      if (data.id) {
        this.updatescramblesgame(wallet, data)
      } else {
        this.createscramblesgame(wallet, data)
      }
    },
    updatescramblesgame: function (wallet, data) {
      var self = this

      LNbits.api
        .request(
          'PUT',
          '/scrambles/api/v1/games/' + data.id,
          wallet.adminkey,
          _.pick(
            data,
            'title',
            'top_left',
            'bottom_right'
          )
        )
        .then(function (response) {
          self.scramblesgames = _.reject(self.scramblesgames, function (obj) {
            return obj.id === data.id
          })
          self.scramblesgames.push(mapscramblesgame(response.data))
          self.formDialog.show = false
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    createscramblesgame: function (wallet, data) {
      var self = this

      LNbits.api
        .request('POST', '/scrambles/api/v1/games', wallet.adminkey, data)
        .then(function (response) {
          self.scramblesgames.push(mapscramblesgame(response.data))
          self.formDialog.show = false
          self.simpleformDialog.show = false
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    deletescramblesgame: function (gameId) {
      var self = this
      var game = _.findWhere(this.scramblesgames, {id: gameId})

      LNbits.utils
        .confirmDialog('Are you sure you want to delete this scrambles game?')
        .onOk(function () {
          LNbits.api
            .request(
              'DELETE',
              '/scrambles/api/v1/games/' + gameId,
              _.findWhere(self.g.user.wallets, {id: game.wallet}).adminkey
            )
            .then(function (response) {
              self.scramblesgames = _.reject(self.scramblesgames, function (obj) {
                return obj.id === gameId
              })
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error)
            })
        })
    },
    exportCSV: function () {
      LNbits.utils.exportCSV(this.paywallsTable.columns, this.paywalls)
    }
  },
  created: function () {
    if (this.g.user.wallets.length) {
      var getscramblesgames = this.getscramblesgames
      getscramblesgames()
      this.checker = setInterval(function () {
        getscramblesgames()
      }, 20000)
    }
  }
})