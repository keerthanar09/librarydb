from django.shortcuts import render, redirect
import mysql.connector as sql
from django.http import HttpResponse
from .models import Student, AdminInfo, BookInfo, OtherBooks, BorrowInfo
from .filters import bookfilter
s_usn = ''
spassword = ''
username = ''
password = ''
#login for admins
def index(request):
    global username, password
    if request.method == "POST":
        m=sql.connect(host="localhost", user="root", passwd="chatterbox123", database="library")
        cursor=m.cursor()
        d = request.POST
        for key, value in d.items():
            if key == "username":
                username = value
            if key == "password":
                password = value

        c = "select * from admin_info where adm_name = '{}' and adm_password = '{}'".format(username, password)
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        if t==():
            return render(request, "library/error.html")
        else:
            return render(request, "library/admin.html")
        
    return render(request, "library/login.html")

#login for students
def login2(request):
    global s_usn, spassword
    if request.method == "POST":
        m=sql.connect(host="localhost", user="root", passwd="chatterbox123", database="library")
        cursor=m.cursor()
        d = request.POST
        for key, value in d.items():
            if key == "s_usn":
                s_usn = value
            if key == "spassword":
                spassword = value

        c = "select * from student where s_usn = '{}' and spassword = '{}'".format(s_usn, spassword)
        cursor.execute(c)
        t=tuple(cursor.fetchall())
        if t==():
            return render(request, "library/error.html")
        else:
            return render(request, "library/student.html")
        
    return render(request, "library/login2.html")
    
        
            
# Create your views here.

def admin(request):
    return render(request, "library/admin.html")

def student(request):
    return render(request, "library/student.html")

def booklist(request):
    books = BookInfo.objects.raw("(select  book_id, isbn, title, authors, rack_no, categoty from book_info) UNION (select ob_id, issn, title, authors, rack_no, category from other_books);")
    myfilter = bookfilter()
    context = {
        'books': books,
        'myfilter': myfilter
    }
    
    return render(request, "library/booklist.html", context)

def studetails(request):
    students = Student.objects.all()
    context = {
        'students' : students
    }
    return render(request, "library/studetails.html", context)

def borrow(request):
    borrow = BorrowInfo.objects.all()
    context = {
        'borrow': borrow
    }
    return render(request, "library/bordetails.html", context)

def addbook(request):

    if request.method == "POST":
        isbn = request.POST['isbn']
        book_id = request.POST['bookid']
        title = request.POST['title']
        authors = request.POST['authors']
        rack_no = request.POST['rack']
        category = request.POST['category']

        new_book = BookInfo(isbn = isbn, book_id = book_id, title = title, authors = authors, rack_no = rack_no, categoty = category)
        new_book.save()
    return render(request, "library/addbook.html")

def addjm(request):
    if request.method == "POST":
        ob_id = request.POST['ob_id']
        issn = request.POST['issn']
        ob_type = request.POST['type']
        issue_date = request.POST['issue']
        title = request.POST['title']
        authors = request.POST['authors']
        category = request.POST['category']
        rack_no = request.POST['rack']

        new_jm = OtherBooks(ob_id = ob_id, issn = issn, ob_type = ob_type, issue_date = issue_date, title = title, authors = authors, category = category, rack_no = rack_no)
        new_jm.save()
    return render(request, "library/addjm.html")

def addstudent(request):

    if request.method == "POST":
        s_usn = request.POST['usn']
        student_name = request.POST['name']
        age = request.POST['age']
        branch = request.POST['branch']
        sem = request.POST['sem']
        lib1 = request.POST['card1']
        lib2 = request.POST['card2']
        phno = request.POST['phno']
        spassword = request.POST['password']

        new_stu = Student(s_usn = s_usn, student_name = student_name, age= age, branch = branch, sem = sem, lib_card_no_1 = lib1, lib_card_no_2 = lib2, phno = phno, spassword = spassword)
        new_stu.save()
    return render(request, "library/addstudent.html")

def check(request):
    global s_usn
    if request.method == "POST":
        d = request.POST
        for key, value in d.items():
            if key == "s_usn":
                s_usn = value
        borrow = BorrowInfo.objects.raw('''select trans_id, b.s_usn, b.return_status, b.lcard, b.due_date 
            from borrow_info b, student s 
            where b.s_usn = '{}' and  (s.s_usn = b.s_usn 
			and (b.lcard = s.Lib_card_no_1 and return_status = 'Not Returned')
            or (b.lcard = s.Lib_card_no_2 and return_status = 'Not Returned'));'''.format(s_usn))
        count = len(borrow)
        if count == 0 or count == 1:
            return redirect('addborrow')
        else:
            return render(request, "library/Cannotborrow.html", {'usn':s_usn, 'borrow':borrow})
    return render(request, "library/check.html")

def checkjm(request):
    global s_usn
    if request.method == "POST":
        d = request.POST
        for key, value in d.items():
            if key == "s_usn":
                s_usn = value
        borrow = BorrowInfo.objects.raw('''select trans_id, b.s_usn, b.return_status, b.lcard, b.due_date 
            from borrow_info b, student s 
            where b.s_usn = '{}' and  (s.s_usn = b.s_usn 
			and (b.lcard = s.Lib_card_no_1 and return_status = 'Not Returned')
            or (b.lcard = s.Lib_card_no_2 and return_status = 'Not Returned'));'''.format(s_usn))
        count = len(borrow)
        if count == 0 or count == 1:
            return redirect('addborjm')
        else:
            return render(request, "library/Cannotborrow.html", {'usn':s_usn, 'borrow':borrow})
    return render(request, "library/checkjm.html")


def addborrow(request):
    if request.method == "POST":
        s_usn = request.POST['usn']
        lcard = request.POST['libcard']
        sname = request.POST['name']
        isbn_or_issn = request.POST['isbn']
        issue_date = request.POST['issuedate']
        due_date = request.POST['duedate']
        admin = request.POST['adid']
        b = request.POST['bi']
        return_status = request.POST['status']
        new_bor = BorrowInfo(s_usn = Student.objects.get(s_usn = s_usn), lcard = lcard, sname = sname, 
                            isbn_or_issn = isbn_or_issn, issue_date = issue_date, due_date = due_date,
                            admin = AdminInfo.objects.get(aid = admin), 
                            b = BookInfo.objects.get(book_id = b), return_status = return_status)
        new_bor.save()


    return render(request, "library/addborrow.html")

def addborjm(request):
    if request.method == "POST":
        s_usn = request.POST['usn']
        lcard = request.POST['libcard']
        sname = request.POST['name']
        isbn_or_issn = request.POST['isbn']
        issue_date = request.POST['issuedate']
        due_date = request.POST['duedate']
        admin = request.POST['adid']
        ob = request.POST['ob']
        return_status = request.POST['status']
        new_bor = BorrowInfo(s_usn = Student.objects.get(s_usn = s_usn), lcard = lcard, sname = sname, 
                            isbn_or_issn = isbn_or_issn, issue_date = issue_date, due_date = due_date,
                            admin = AdminInfo.objects.get(aid = admin), 
                            ob = OtherBooks.objects.get(ob_id = ob), return_status = return_status)
        new_bor.save()

    return render(request, "library/addborjm.html")

def updborrow(request):
    return render(request, "library/updborrow.html")

def trending(request):
    
    books = BorrowInfo.objects.raw('''select trans_id, title, count(br.isbn_or_issn) as borrow_count 
                                  from borrow_info br 
                                  join book_info b on b.book_id = br.b_id 
                                 Group by b.title 
                                 order by borrow_count desc
                                   limit 10''')
    context = {
        'books': books
    }
    return render(request, "library/trending.html", context)

def booksstu(request):
    books = BookInfo.objects.raw("(select  book_id, isbn, title, authors, rack_no, categoty from book_info) UNION (select ob_id, issn, title, authors, rack_no, category from other_books);")
    context = {
        'books': books
    }
    return render(request, "library/booksstu.html", context)

