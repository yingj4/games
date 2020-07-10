# coding:utf-8

from flask import Flask, render_template, flash, redirect, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import random
from datetime import datetime


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ConfigForm(FlaskForm):
    civil = StringField('civil')
    evil = StringField('evil')
    tolerance = BooleanField('tolerance')
    quest = StringField('quest')
    command = StringField('command')
    name = StringField('name')
    submit = SubmitField('Submit')

class VoteForm(FlaskForm):
    good = BooleanField('pass')
    submit = SubmitField('Submit')

class QuestForm(FlaskForm):
    good = BooleanField('pass')
    submit = SubmitField('Submit')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'


class Game():
    def __init__(self):
        self.msg = ''
        self.roles = []
        self.users = {}
        self.user_attributes = {}
        self.max_num = 0
        self.count = 0
        self.tolerance = False
        self.votes = {}
        self.voting = False
        self.quests = []
        self.questing = False
        self.quest_idx = 0
        self.quests_num = []
        self.base_msg = ''
        self.vote_msg = ''
        self.user_specific_msg = {}

    def add_user(self, name):
        if self.count == self.max_num:
            return None, None
        ret, attr = self.roles[0]
        ret = ret.decode('utf-8')
        self.roles = self.roles[1:]
        self.count += 1
            
        self.users[self.count] = (name, ret)
        self.user_attributes[self.count] = attr

        if self.count == self.max_num:
            bad = [self.users[a][0] if (self.user_attributes[a] in [2, 3, 5]) else '' for a in self.user_attributes]
            god = [self.users[a][0] if (self.user_attributes[a] in [0, 2]) else '' for a in self.user_attributes]
            for p in self.users:
                if self.user_attributes[p] == 0: # merlin
                    self.user_specific_msg[p] = 'Bad players: ' + str(bad)
                elif self.user_attributes[p] == 1: # parcevil
                    self.user_specific_msg[p] = 'Possible Merlin: ' + str(god)
                elif self.user_attributes[p] in [2, 3, 5]: # bad guys
                    self.user_specific_msg[p] = 'Evil Mates: ' + str(bad)
                else:
                    pass
        return self.count, ret


    def config(self, civil, evil, tolerance, quest):
        self.msg = ''
        self.votes = {}
        self.count = 0
        self.tolerance = tolerance
        self.num = 4 + civil + evil
        self.voting = False
        self.questing = False
        self.quest_idx = 0
        self.quests_num = [int(a.strip()) for a in quest.split(',')]
        self.base_msg = ''
        self.vote_msg = ''
        self.user_specific_msg = {}
        self.user_attributes = {}
        self.roles = [(u'梅林'.encode('utf-8'), 0), (u'派西維爾'.encode('utf-8'), 1), (u'莫幹那'.encode('utf-8'), 2), (u'刺客'.encode('utf-8'), 3)]
        for i in range(civil):
            self.roles.append((u'平民'.encode('utf-8'), 4))
        for i in range(evil):
            self.roles.append((u'壞人平民'.encode('utf-8'), 5))
        random.seed(datetime.now())
        random.shuffle(self.roles)
        print(self.roles)
        self.max_num = len(self.roles)
        print(self.to_string())

    def vote(self, uname, good):
        self.voting = True
        self.votes[uname] = good
        if len(self.votes) == self.max_num:
            self.refresh_game_msg()

    def quest(self, uname, good):
        self.questing = True
        self.quests.append(good)
        if len(self.quests) == self.quests_num[self.quest_idx]:
            self.refresh_game_msg()
            self.quest_idx += 1


    def refresh_game_msg(self):
        s = ''
        if len(self.votes) == self.max_num:
            s = self.base_msg
            for i in range(self.quest_idx, 5):
                s += '[{}*]'.format(self.quests_num[i]) if self.tolerance and i == 3 else '[{}]'.format(self.quests_num[i])
 
            res = sum([1 if self.votes[a] else 0 for a in self.votes])
            self.vote_msg = '[{}]'.format('Vote result is PASS' if res > len(self.votes)/2 else 'Vote result is FAIL')
            self.vote_msg += ' | '
            for p in self.votes:
                self.vote_msg += p
                self.vote_msg += ' voted {}'.format('pass' if self.votes[p] else 'fail')
                self.vote_msg += ' | '
            self.votes = {}
            self.voting = False
            self.vote_msg
            s += self.vote_msg

        elif len(self.quests) == self.quests_num[self.quest_idx]:
            res = sum([0 if a else 1 for a in self.quests])
            if self.tolerance and self.quest_idx == 3:
                res -= 1
            self.quests = []
            self.questing = False
            self.base_msg += '[{}]'.format('X' if res > 0 else u'✓')
            s = self.base_msg
            for i in range(self.quest_idx+1, 5):
                s += '[{}*]'.format(self.quests_num[i]) if self.tolerance and i == 3 else '[{}]'.format(self.quests_num[i])
            s += '<br>' + self.vote_msg

        self.msg = s

    def get_game_msg(self, uid):
        s = ''
        try:
            s = self.user_specific_msg[uid]
        except:
            pass
        return self.msg + '<br>' + s
    

    def to_string(self):
        return 'Avalon Game\nTotol Players {max_num}\nTolerance {tolerance}'.format(**self.__dict__)

game = Game()

@app.route('/')
def home():
    return u'<h1>Please wait until host tells you to login. Username cannot be the same as other players. Host should login as admin. Please keep page open. Wechat floating window is supported. Host can re-login as admin to start next game.</h1><br><h1><a href="/login"> click here to login </a></h1><h1>Copyright © Zeran Zhu 2020, All rights reserved.</h1>'

@app.route('/view_vote_result')
def view_vote_result():
    uid = int(request.args.get('uid'))
    while game.voting:
        pass
    return redirect('/play?uid={}'.format(uid))

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    uid = int(request.args.get('uid'))
    uname, role = game.users[uid]
    form = VoteForm()
    if form.validate_on_submit():
        good = form.good.data
        game.vote(uname, good)
        return redirect('/view_vote_result?uid={}'.format(uid))
    return render_template('vote.html', title='Vote as {}'.format(uname), form=form)

@app.route('/view_quest_result')
def view_quest_result():
    uid = int(request.args.get('uid'))
    while game.questing:
        pass
    return redirect('/play?uid={}'.format(uid))

@app.route('/quest', methods=['GET', 'POST'])
def quest():
    uid = int(request.args.get('uid'))
    uname, role = game.users[uid]
    form = QuestForm()
    if form.validate_on_submit():
        good = form.good.data
        game.quest(uname, good)
        return redirect('/view_quest_result?uid={}'.format(uid))
    return render_template('quest.html', title='Quest as {}'.format(uname), form=form)


@app.route('/play')
def show():
    while game.voting or game.questing:
        pass
    uid = int(request.args.get('uid'))
    uname, role = game.users[uid]

    return u'<h1>Online BoardGames</h1><h1>Copyright © Zeran Zhu 2020, All rights reserved.</h1><h2>Welcome {}</h2><h2>You are player #{}</h2><h2>Your role is {}</h2><h2>{}</h2><h2><a href="/vote?uid={}">Vote!</a></h2><h2><a href="/quest?uid={}">Quest!</a></h2><br><br><h2><a href="/play?uid={}">Refresh page</a></h2>'.format(uname, uid, role, game.get_game_msg(uid), uid, uid, uid)


@app.route('/config', methods=['GET', 'POST'])
def conf():
    form = ConfigForm()
    if form.validate_on_submit():
        print(form.civil.data, form.evil.data)
        civil = int(form.civil.data)
        evil = int(form.evil.data)
        tolerance = form.tolerance.data
        quest = form.quest.data
        uname = form.name.data
        game.config(civil, evil, tolerance, quest)
        uid, role = game.add_user(uname)
        return redirect('/play?uid={}'.format(uid))
    return render_template('config.html', title='Game', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        if form.username.data == 'admin':
            return redirect('/config')
        else:
            uid, role = game.add_user(form.username.data)
            return redirect('/play?uid={}'.format(uid))
    return render_template('login.html', title='Sign In', form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5800)

