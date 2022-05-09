import csv
import logging
import os

from flask import Blueprint, render_template, abort, url_for, current_app
from flask_login import current_user, login_required
from jinja2 import TemplateNotFound

from app.db import db
from app.db.models import Transaction
from app.db.models import User
from app.transactions.forms import csv_upload
from werkzeug.utils import secure_filename, redirect
from app.auth import auth

transactions = Blueprint('transactions', __name__,
                         template_folder='templates')


@transactions.route('/transactions', methods=['GET'], defaults={"page": 1})
@transactions.route('/transactions/<int:page>', methods=['GET'])
@login_required
def transactions_browse(page):
    page = page
    per_page = 1000
    pagination = Transaction.query.filter_by(user_id=current_user.id).paginate(page, per_page, error_out=False)
    user_object = User.query.get(current_user.id)
    user_balance = user_object.balance
    data = pagination.items
    try:
        return render_template('browse_transactions.html', data=data, pagination=pagination, user_balance=user_balance)
    except TemplateNotFound:
        abort(404)


@transactions.route('/transactions/upload', methods=['POST', 'GET'])
@login_required
def transactions_upload():
    form = csv_upload()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        # writing a log into the uploads.log file everytime a csv file is uploaded.
        log = logging.getLogger("uploads")
        log.info('csv upload successful!')
        filename = secure_filename(form.file.data.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        form.file.data.save(filepath)
        list_of_transactions = []
        with open(filepath) as file:
            csv_file = csv.DictReader(file)
            for row in csv_file:
                # list_of_transactions.append(Transaction(user.id, row['AMOUNT'], row['TYPE']))

                transaction = Transaction.query.filter_by(amount=row['AMOUNT']).first()
                if transaction is None:
                    current_user.transaction.append(
                        Transaction(row['AMOUNT'], row['TYPE']))
                    db.session.commit()
                else:
                    current_user.transactions.append(transaction)
                    db.session.commit()



        # user.transactions = list_of_transactions
        # db.session.commit()
        update_balance()
        return redirect(url_for('transactions.transactions_browse'))

    try:
        return render_template('upload.html', form=form)
    except TemplateNotFound:
        abort(404)


def update_balance():
    user = User.query.get(current_user.id)
    user_transactions = Transaction.query.filter_by(user_id=user.id).all()

    balance = user.balance if user.balance is not None else 0
    for transaction in user_transactions:
        if transaction.transaction_type == 'CREDIT':
            balance = balance + transaction.amount
        if transaction.transaction_type == 'DEBIT':
            balance = balance - transaction.amount

    user.balance = balance
    db.session.commit()
    return