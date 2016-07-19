from flask import Blueprint, render_template, current_app

main_blueprint = Blueprint('main', __name__, template_folder='templates')


@main_blueprint.route('/')
def main_page():

    return render_template('main.html', config=current_app.config)
