from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send
from threading import Thread
from Generator import Generator
import json    

class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='<<',
        variable_end_string='>>',
        comment_start_string='<#',
        comment_end_string='#>',
    ))

app = CustomFlask(__name__)
socketio = SocketIO(app)

def generate_bots():
    bots = []
    for i in range(10):
        bots.append(Generator(a=i))
    return bots

bots = generate_bots()

@socketio.on('reload-bots')
def get_bots():
    bots_statuses = []
    for bot in bots:
        bots_statuses.append({
            'id': bot.id,
            'ident': bot.ident,
            'timeout': bot.timeout_in_seconds,
            'is_alive': bot.is_alive(),
            'running_for': round(bot.time_count, 2),
            'max': bot.max,
            'min': bot.min,
            'value': bot.value,
            'sleep_delay': bot.sleep_delay,
            'generated_values': bot.vault,
            'history_size': bot.vault_size,
            'killed': bot.please_kill_me
        })
    emit('load-all-bots', bots_statuses, json=True, broadcast=True)

@socketio.on('create-bot')
def create_bot(c_bot):
    b = Generator(int(c_bot['min']), int(c_bot['max']), float(c_bot['timeout']), int(c_bot['history_size']))
    b.sleep_delay = float(c_bot['sleep_delay'])
    return b.id

@socketio.on('update-bot')
def update_bot(c_bot):
    for bot in bots:
        if bot.id == c_bot['id']:
            bot.min = int(c_bot['min'])
            bot.max = int(c_bot['max'])
            bot.timeout_in_seconds = float(c_bot['timeout'])
            bot.sleep_delay = float(c_bot['sleep_delay'])
            bot.vault_size = int(c_bot['history_size'])
            return True
    return False

@socketio.on('start-bot')
def start_bot(bot_id):
    for bot in bots:
        if bot.id == bot_id:
            bot.start()
            return json.dumps(bot.ident)
    return False

@socketio.on('stop-bot')
def stop_bot(bot_id):
    for bot in bots:
        if bot.id == bot_id:
            bot.please_kill_me = True
            bots.remove(bot)
            return True
    return False

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')