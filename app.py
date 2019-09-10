from flask import Flask,render_template,url_for, redirect,request, flash 
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required #로그인시에 쓰임 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from flask_migrate import Migrate # db 수정용 pip install flask-migrate 먼저 해야함 
from datetime import datetime #DB 에 create 데이 찍을려고 
from flask_wtf import FlaskForm # form  밸리데이트 하기위해 
from wtforms import StringField, SubmitField, PasswordField # 폼에 validate 할때 쓰이는 필드들 
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length


#setting
app=Flask(__name__)
app.secret_key="total secret"

#로그인 세팅
login=LoginManager(app)
login.login_view="login"

#DB 세팅
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
db=SQLAlchemy(app)
migrate=Migrate(app,db)# db수정하기위해 만듬 



class Users(UserMixin, db.Model): # 유저 테이블 정의 
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True)
    password_hash=db.Column(db.String,nullable=False)
    username=db.Column(db.String, unique=True)
    posts = db.relationship("Posts", backref="users", lazy="dynamic") # 다른테이블과의 관계정의 
    comments = db.relationship("Comments", backref="users", lazy="dynamic")

    def set_password(self, password):  # 패스워드를 그대로 저장하는게아닌 해쉬함수로 암호화시켜서 저장하기 때문에 필요 
        self.password_hash=generate_password_hash(password)
    
    def check_password(self, password): #내가 입력한 패스워드가 디비에 저장된 값과 같은지 확인하기위해 만듬 
        return check_password_hash(self.password_hash,password)

class Posts(db.Model): #게시글 테이블 정의 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)
    author =  db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    view=db.Column(db.Integer, default=0)
    comments = db.relationship('Comments', backref="posts", lazy="dynamic")
    view=db.Column(db.Integer, default=0)
     
class Comments(db.Model): # 댓글 테이블 정의
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)
    author =  db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)

class Flags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer, nullable=False )
    post_id=db.Column(db.Integer, nullable=False)
    created= db.Column(db.DateTime, nullable=False)

db.create_all()  #DB 테이블 생성

@login.user_loader #질문 
def load_user(user_id):
    return Users.query.get(user_id)

#form 들 정의
class Register(FlaskForm): # 회원가입시 이메일이 유니크인지 유저내임에 유니크인지 패스워드와 컨펌 패스워드가 같은지 확인 
    username=StringField("User name", validators=[DataRequired("please input your user name"), Length(min=3, max=20, message="username must have at least 3 char and max 20 chars")])
    email=StringField("Email address", validators=[DataRequired(),Email("please input an appropriate email address")])
    password=StringField("password", validators=[DataRequired(),EqualTo("confirm")])
    confirm=StringField("confirm password", validators=[DataRequired()])
    submit=SubmitField("register")

    def validate_username(self,field): #유저내임 유니크인지 확인 
        if Users.query.filter_by(username=field.data).first():
            raise ValidationError("your name has been registered")
    def validate_email(self, field):# 이메일이 유니크인지 확인 
        if Users.query.filter_by(email=field.data).first():
            raise ValidationError("your email has been registerd")

class Login(FlaskForm): # 로그인 시에 확인해야되는 폼 
    email=StringField("Email address", validators=[DataRequired(),Email("please input an appropriate email address")])
    password=StringField("password", validators=[DataRequired()])
    submit=SubmitField("Login")

class Post(FlaskForm):
    title=StringField("Title", validators=[DataRequired("please input the title"),Length(min=1, max=100,message="username must have at least 1 char and max 100 chars")])
    body=StringField("Body",validators=[DataRequired()])
    submit=SubmitField("post")

class Comment(FlaskForm):
    body=StringField("Body",validators=[DataRequired()])



@app.route('/register', methods=['POST','GET']) #회원가입 화면 
def register():
    form=Register()
    if request.method=="POST":
        if form.validate_on_submit():
            new_user=Users(username=form.username.data,
                           email=form.email.data,)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            for field_name,errors in form.errors.items():
                flash(errors,'danger')
                return redirect(url_for('register'))
    return render_template('register.html',form=form)

@app.route('/login', methods=['post','get']) #로그인화면 
def login():
    form=Login()
    if request.method=="POST":
       
        check=Users.query.filter_by(email=form.email.data).first()
       
        print(check,"==========================================")
        if check:
            if check.check_password(form.password.data):
                login_user(check)
                return redirect(url_for('home'))
            else:
                flash('wrong password','danger')
                return redirect(url_for('login'))
        else:
             flash('can not find this user','danger')
             return redirect(url_for('register'))
    return render_template('login.html',form=form)

@app.route('/home') # 처음 홈화면 
def home():
    data=Posts.query.filter_by().all()
    return render_template('home.html',data=data)

@app.route('/post', methods=['POST','GET']) #포스트 화면 
def post():
    form=Post()
    if request.method=="POST":
        new_post=Posts(title=form.title.data,
                       body= form.body.data,
                       author=current_user.id,
                       created=datetime.now()) #datetime  사용법 
        db.session.add(new_post)
        db.session.commit()
        flash("successfully posted",'success')
        return redirect(url_for('home'))
    return render_template('post.html',form=form)

@app.route('/posts/<post_id>', methods=['POST','GET']) # 디테일 포스트들을 보는곳 
def detail(post_id):
    
    data=Posts.query.filter_by(id=post_id).first()
    check=Posts.query.filter_by(id=post_id).first()
    check.view += 1
    db.session.commit()
    return render_template('details.html',data=data)

@app.route('/report/<post_id>')
def report(post_id):
    data=Flags.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if data:
        flash("you already reort this post chill",'danger')
    else:

        report=Flags(user_id=current_user.id, post_id=post_id, created=datetime.now())
        db.session.add(report)
        db.session.commit()
        flash('Your report has been sent', 'success')
  
    return redirect(url_for('home'))

@app.route('/posts/<post_id>/comments', methods=['POST','GET']) # 코멘트달기 
def comment(post_id):
     form=Comments()
     if request.method=="POST":
          if form.validate_on_submit():
              post=Posts.query.filter_by(id=post_id).first()
              c=Comments(form.body.data,
                         created =datetime.now(),
              )
              current_user.comments.append(c)
              post.comments.append(c)
              db.session.add(c)
              db.session.commit()
              return  redirect(url_for('detail', post_id=post_id))
          else:
             for field_name, errors in form.errors.items():
                 flash(errors,'danger')
                 return redirect((url_for('comment')))
     return render_template('new_comment.html', form = form)

    



@app.route('/logout') # 로그아웃 
def logout():
    logout_user()
    flash("please come back again ",'info')
    return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)