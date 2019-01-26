# microblog
This project is intended for a personal blog powered by flask.

for Windows:
1.git clone this .git
2.enter the microblog directory
3.set FLASK_APP=microblog.py (though you can directly execute "python microblog.py".but it's not a good habbit for latter work.)
4.set FLASK_ENV=development (enter debug mode,not necessary)
5.flask run 


These files may not be wrote in a lucid style now,I will try to adjust them,so..emm
some other matters you maybe need to know if you are not familiar with flask web:
  (1) Don't forget set environment params,such as FLASK_APP and any params in config.py
  (2) >>>flask db migrate -m "some messages",then
      >>>flask db upgrade
  (3) flask shell 
  
  
  
