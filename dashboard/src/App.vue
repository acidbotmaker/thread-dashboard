<template>
  <div id="app">
    <h1>Simple Thread Controller</h1>
    <div>
      <input type="hidden" id="copy2clipboard" :value="clipboardContent">
      <b-button-toolbar key-nav aria-label="Bot controller toolbar">
        <b-button-group class="mx-1">
          <b-button class="btn btn-success" v-on:click="prepareForm">Add new</b-button>
        </b-button-group>
        <b-button-group class="mx-1">
          <b-button class="btn btn-info" v-on:click="reload">Reload</b-button>
        </b-button-group>
      </b-button-toolbar>
      <div class="col-lg-3">
        <label class="control-label">Poll Interval <b>{{ poll_interval/1000 }}</b> seconds</label>
        <br />
        <b-form-input type="range" v-model="poll_interval" min="100" max="10000" step="1"  v-on:change="reload"/>
      </div>
    </div>

    <div v-if="showForm" id="add-bot" title="Add new Bot" class="col-md-6">
      <div class="bot-form-container">
        <div class="form-row">
          <div class="form-group col">
            <label class="control-label">Min value</label>
            <input placeholder="Minimum value" min="1" max="50000" v-model="new_bot.min" class="form-control" required="true" type="number">
          </div>
          <div class="form-group col">
            <label class="control-label">Max value</label>
            <input placeholder="Maximum value"  min="1" max="50000" v-model="new_bot.max" class="form-control" required="true" type="number">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group col">
            <label class="control-label">Timeout (in seconds)</label>
            <input placeholder="Time in seconds" v-model="new_bot.timeout" class="form-control" required="true" type="text">
          </div>
          <div class="form-group col">
            <label class="control-label">Sleep delay for <b>{{ new_bot.sleep_delay }}</b> seconds</label>
            <br />
            <b-form-input type="range" v-model="new_bot.sleep_delay" min="0.1" max="10" step="0.1" />
          </div>
        </div>
        <div class="form-row">
          <div class="col-md-4">
            <label class="control-label">Bucket Size</label><br/>
            <input v-model="new_bot.history_size" class="form-control" required="true" type="number">
          </div>
          <div class="col-md-3">
            <b-button
              variant="primary"
              size="sm"
              class="float-right"
              @click="addBot(new_bot)"
            >Add new Bot
            </b-button>
          </div>
        </div>
      </div>
    </div>

    <hr />
    <div>
      <b-row v-if="bots.length == 0">
        <b-card>
          No bots found
        </b-card>
      </b-row>
      <b-row v-else>
        <b-table 
          v-if="tableIsReady"
          striped hover responsive flex
          
          :fields="fields"
          :items="bots"

          @row-clicked="showDetails"
        >
        
          <template slot="selected">
            <b-form-checkbox></b-form-checkbox>
          </template>

          <template slot="status" slot-scope="data">
            <span v-b-tooltip.hover :title="data.item.ident">
              {{ data.item.id }}
            </span>
            <b-badge v-if="data.item.is_alive" variant="success">Running</b-badge>
            <b-badge v-else variant="danger">Stopped</b-badge>
          </template>

          <template slot="value_" slot-scope="data">
            ( {{ data.item.min }}, {{ data.item.max }} ) => {{ data.item.value }}
            
            <b-badge pill variant="primary" v-on:click="copyValue(data.item.value)">Copy</b-badge>
          </template>

          <template slot="operation" slot-scope="data">
            <div v-if="!data.item.killed">
              <b-button v-if="!data.item.is_alive" variant="success" v-on:click="startBot(data.item.id)">Launch</b-button>
              <b-button v-else variant="danger" v-on:click="stopBot(data.item.id)">Stop</b-button>
            </div>
          </template>
        </b-table>
        <b-modal v-if="showInfo" id="more-info" :title="'Bot #' + current_bot.id" lg>
          <div class="bot-form-container">
            <div class="form-row">
              <div class="form-group col">
                <label class="control-label">Min value</label>
                <input placeholder="Minimum value" min="1" max="50000" v-model="current_bot.min" class="form-control" required="true" type="number" :disabled="current_bot.killed">
              </div>
              <div class="form-group col">
                <label class="control-label">Max value</label>
                <input placeholder="Maximum value"  min="1" max="50000" v-model="current_bot.max" class="form-control" required="true" type="number" :disabled="current_bot.killed">
              </div>
              <div class="form-group col">
                <label class="control-label">Current value</label>
                <b-form-input v-model="current_bot.value" readonly />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group col">
                <label class="control-label">Timeout (in seconds)</label>
                <input placeholder="Time in seconds" v-model="current_bot.timeout" class="form-control" required="true" type="text" :disabled="current_bot.killed">
              </div>
              <div class="form-group col">
                <label class="control-label">Sleep delay for <b>{{ current_bot.sleep_delay }}</b> seconds</label>
                <br />
                <b-form-input type="range" v-model="current_bot.sleep_delay" min="0.1" max="10" step="0.1" :disabled="current_bot.killed" />
              </div>
            </div>
            <div class="form-row" v-if="current_bot.running_for > 0">
              <div class="form-group col">
                <label class="control-label">Progress 
                  <b v-if="current_bot.timout > 0">{{ this.get_completion_percent(current_bot.timeout, current_bot.running_for) }}%</b>
                  <b v-else>∞</b>
                </label>
                <b-progress :value="get_completion_percent(current_bot.timeout, current_bot.running_for)" variant="success" striped animated :disabled="current_bot.killed"></b-progress>
              </div>
            </div>
            <div class="form-row">
              <label class="control-label">Bucket Size</label>
            </div>
            <div class="form-row">
              <div class="col-md-3">
                <input v-model="current_bot.history_size" class="form-control" required="true" type="number" :disabled="current_bot.killed">
              </div>
              <div class="col-md-9">
                <i>{{ current_bot.generated_values.join(',') }}</i>
              </div>  
            </div>
          </div>

          <div slot="modal-footer" class="w-100">
            <b-button
              variant="primary"
              size="sm"
              class="float-right"
              @click="updateBot(current_bot.id)"
            >Update
            </b-button>
          </div>
        </b-modal>
      </b-row>
    </div>
  </div>
</template>

<script>  
import io from 'socket.io-client';
import { timeout } from 'q';

export default {
  name: "app",
  components: {
  },
  data () {
    return {
      tableIsReady: true,
      fields: [
        //{ key:'selected', label: ''},
        { key:'status', label: 'Bot ID'},
        { key: 'running_for', label: 'Runtime', sortable: true},
        { key: 'value_', label: 'Value' },
        { key: 'operation', label: 'Operation' }
      ],
      bots: [],
      interval: null,
      showForm: false,
      socket : null,
      current_bot: null,
      new_bot: null,
      showInfo: false,
      clipboardContent: '',
      poll_interval: 100
    }
  },
  methods: {
    startBot (bot_id) {
      this.socket.emit('start-bot', bot_id, (response) => {
        if(response == false){
          alert("Bot didn't start")
        }
      });
    },
    stopBot (bot_id) {
      this.socket.emit('stop-bot', bot_id, (response) => {
        if(response == false){
          alert("Bot didn't stop")
        }
      });
    },
    copyValue(val){
      this.clipboardContent = val;
      
      const copy_element = document.querySelector('#copy2clipboard')
      copy_element.setAttribute('type', 'text')

      window.getSelection().removeAllRanges()
      copy_element.select()

      try {
        var successful = document.execCommand('copy');
        var msg = successful ? 'successful' : 'unsuccessful';
      } catch (err) {
        alert('Oops, unable to copy');
      }

      window.getSelection().removeAllRanges()
    },
    showDetails (row) {
      this.current_bot = row
      this.showInfo = true
      this.$bvModal.show('more-info')
    },
    reload () {
      this.socket.emit('reload-bots')
      console.log(this.bots)
      clearInterval(this.interval)
      this.interval = setInterval(() => {
        this.socket.emit('reload-bots')
      }, this.poll_interval)
    },
    get_completion_percent(timeout, completed){
      if(timeout <= 0)
        return 100
      return (completed / timeout) * 100;
    },
    prepareForm () {
      this.showForm = !this.showForm;
      this.new_bot = {
        min: 1,
        max: 50000,
        timeout: -1,
        history_size: 10,
        sleep_delay: 0.1
      }
      this.$bvModal.show('add-bot')
    },
    addBot (bot) {
      this.socket.emit('create-bot', bot, (response) => {
        if(response == false){
          alert("Failed to create a bot")
        }
        this.showForm = false;
      });
    },
    updateBot () {
      this.socket.emit('update-bot', this.current_bot, (response) => {
        if(response == false){
          alert("Failed to updated the bot")
        }
        this.$bvModal.hide('more-info')
      });
    }
  },
  created () {
    this.socket = io("http://localhost:5001");
  },
  mounted () {
    this.socket.on('load-all-bots', (data) => {
      this.bots = data
      this.tableIsReady = true
    });
    
    this.interval = setInterval(() => {
      this.socket.emit('reload-bots')
    }, this.poll_interval);
  }
};
</script>

<style lang="scss">
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin: 20px;
}
#copy2clipboard{
  display: none;
}
</style>
