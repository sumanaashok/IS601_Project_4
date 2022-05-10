import logging

from app import db
from app.db.models import User, Transaction
from faker import Faker


def test_adding_user(application):
    log = logging.getLogger("myApp")
    with application.app_context():
        assert db.session.query(User).count() == 0
        assert db.session.query(Transaction).count() == 0
        #showing how to add a record
        #create a record
        user = User('sbangaloreashok@gmail.com', 'sumanatest')
        #add it to get ready to be committed
        db.session.add(user)
        #call the commit
        db.session.commit()
        #assert that we now have a new user
        assert db.session.query(User).count() == 1
        #finding one user record by email
        user = User.query.filter_by(email='sbangaloreashok@gmail.com').first()
        log.info(user)
        #asserting that the user retrieved is correct
        assert user.email == 'sbangaloreashok@gmail.com'
        #this is how you get a related record ready for insert
        user.transactions = [Transaction("1","2000","CREDIT"),Transaction("2","-1000","DEBIT")]
        #commit is what saves the transactions
        db.session.commit()
        assert db.session.query(Transaction).count() == 2
        transaction1 = Transaction.query.filter_by(transaction_type='CREDIT').first()
        assert transaction1.transaction_type == "CREDIT"
        #changing the title of the song
        transaction1.transaction_type = "DEBIT"
        #saving the new title of the song
        db.session.commit()
        transaction2 = Transaction.query.filter_by(transaction_type='DEBIT').first()
        assert transaction2.transaction_type == "DEBIT"
        #checking cascade delete
        db.session.delete(user)
        assert db.session.query(User).count() == 0
        assert db.session.query(Transaction).count() == 0




