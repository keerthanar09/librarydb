from django.db import models

# Create your models here.

class Student(models.Model):
    s_usn = models.CharField(primary_key=True, max_length=10)
    student_name = models.CharField(max_length=40)
    age = models.IntegerField(blank=True, null=True)
    branch = models.CharField(max_length=60)
    sem = models.IntegerField(blank=True, null=True)
    lib_card_no_1 = models.IntegerField(db_column='Lib_card_no_1', blank=True, null=True)  # Field name made lowercase.
    lib_card_no_2 = models.IntegerField(db_column='Lib_card_no_2', blank=True, null=True)  # Field name made lowercase.
    phno = models.BigIntegerField(db_column='Phno')  # Field name made lowercase.
    spassword = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'student'

class AdminInfo(models.Model):
    aid = models.BigIntegerField(primary_key=True)
    adm_name = models.CharField(max_length=50)
    email = models.CharField(max_length=60)
    adm_password = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin_info'

class BookInfo(models.Model):
    isbn = models.CharField(max_length=50, blank=True, null=True)
    book_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    authors = models.CharField(max_length=100, blank=True, null=True)
    rack_no = models.IntegerField(blank=True, null=True)
    categoty = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'book_info'

class OtherBooks(models.Model):
    ob_id = models.IntegerField(primary_key=True)
    issn = models.CharField(max_length=50, blank=True, null=True)
    ob_type = models.CharField(max_length=100, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    authors = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    rack_no = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'other_books'

class BorrowInfo(models.Model):
    trans_id = models.AutoField(primary_key=True)
    s_usn = models.ForeignKey('Student', models.DO_NOTHING, db_column='s_usn', blank=True, null=True)
    lcard = models.IntegerField(db_column='Lcard', blank=True, null=True)  # Field name made lowercase.
    sname = models.CharField(max_length=50, blank=True, null=True)
    isbn_or_issn = models.CharField(max_length=20, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    return_status = models.CharField(max_length=20, blank=True, null=True)
    admin = models.ForeignKey(AdminInfo, models.DO_NOTHING, blank=True, null=True)
    ob = models.ForeignKey('OtherBooks', models.DO_NOTHING, blank=True, null=True)
    b = models.ForeignKey(BookInfo, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'borrow_info'