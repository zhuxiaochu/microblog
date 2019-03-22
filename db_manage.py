from app import db, app
from app.models import Stats, Post

stats_post = Stats.query.filter_by(name='post_count').first()
if not stats_post:
    post_count = Stats(name='post_count')
    db.session.add (post_count)
    db.session.commit()
else:
    stats_post.value = Post.query.count()

custom_triggers = ['count_up', 'count_down']#up must be first,down  be down
if db.engine.dialect.name == 'mysql':
    triggers = db.engine.execute('show triggers;').fetchall()
    for n in triggers:
        if n[0] in custom_triggers:
            raise Exception("triggers existed {0}".format(n[0]))
    db.engine.execute('''CREATE TRIGGER {0} AFTER INSERT ON 'post' FOR EACH ROW UPDATE 'stats'
        SET 'stats'.'value' = 'stats'.'value' + 1 
        WHERE 'stats'.'name' = "post_count";
        CREATE TRIGGER {1} AFTER DELETE ON 'post' FOR EACH ROW UPDATE 'stats'
        SET 'stats'.'value' = 'stats'.'value' - 1 
        WHERE 'stats'.'name' = 'post_count';'''.format(custom_triggers[0],
            custom_triggers[1]))

