'''
all the cron jobs
'''

import os
from datetime import datetime, timedelta
from app import app, db
from app.models import UploadImage


def clear_image():
    '''delete all the images that marked 0'''
    with app.app_context():
        delete_image = UploadImage.query.filter_by(mark=0).all()
        if delete_image:
            for img in delete_image:
                if datetime.utcnow() - img.upload_time > timedelta(days=5):
                    try:
                        os.remove(img.image_path)
                        db.session.delete(img)
                    except:
                        app.logger.error("can't delete image:"+img.image_path)
            db.session.commit()
            app.logger.warning('Delete all the useless images!')
