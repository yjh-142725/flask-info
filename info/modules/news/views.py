from . import news_blu
from flask import render_template


@news_blu.route('/<int:news_id>')
def news_detail(news_id):
    data = {}
    return render_template('news/detail.html', data=data)