from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import mysql.connector as sql
from django.http import HttpResponse
from .models import Student, AdminInfo, BookInfo, OtherBooks, BorrowInfo
from .filters import bookfilter
from .forms import *
from django.contrib.auth.hashers import check_password
s_usn = ''
spassword = ''
username = ''
password = ''
#login for students.
def student_login(request):
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
            return render(request, "library/errors/error.html")
        else:
            return render(request, "library/student.html")
        
    return render(request, "library/stulogin.html") 


#login for admins
def admin_login(request):
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
            return render(request, "library/errors/error.html")
        else:
            return render(request, "library/admin.html")
        
    return render(request, "library/admlogin.html")
 
# Create your views here.

def admin(request):
    return render(request, "library/admin.html")

def student(request):
    return render(request, "library/student.html")

def booklist(request):
    books = BookInfo.objects.raw("(select  book_id, isbn, title, authors, rack_no, categoty, 'Regular' as book_type from book_info) UNION (select ob_id, issn, title, authors, rack_no, category, ob_type from other_books);")
    
    '''form = BookSearchForm(request.GET or None)

    if form.is_valid():
        query = form.cleaned_data.get('query')
        author = form.cleaned_data.get('author')
        category = form.cleaned_data.get('category')
        isbn = form.cleaned_data.get('isbn')
        if query:
            books = books.filter(title__icontains=query)
        if author:
            books = books.filter(authors__icontains=author)
        if category:
            books = books.filter(category__icontains=category)
        if isbn:
            books = books.filter(isbn__icontains=isbn)'''
    context = {
        'books': books,
       # 'form' : form,
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
        #To check if the student is eligibe to borrow a book.
        borrow = BorrowInfo.objects.raw('''select trans_id, b.s_usn, b.return_status, b.lcard, b.due_date 
            from borrow_info b, student s 
            where b.s_usn = '{}' and  (s.s_usn = b.s_usn 
			and (b.lcard = s.Lib_card_no_1 and return_status = 'Not Returned')
            or (b.lcard = s.Lib_card_no_2 and return_status = 'Not Returned'));'''.format(s_usn))
        #To check for free library cards for students who can borrow a book.
        free = BorrowInfo.objects.raw('''(SELECT MIN(b1.trans_id) AS trans_id, s.Lib_card_no_1 as library_card, s.s_usn
                                        from library.student s
                                        left join library.borrow_info b1
                                        on s.s_usn = b1.s_usn and s.Lib_card_no_1 = b1.lcard
                                        where s.s_usn = '{}' and (b1.lcard is null or b1.return_status = 'Returned'))
                                        union
                                        (SELECT MIN(b2.trans_id) AS trans_id, s.Lib_card_no_2 as library_card, s.s_usn
                                        from library.student s
                                        left join library.borrow_info b2
                                        on s.s_usn = b2.s_usn and s.Lib_card_no_2 = b2.lcard
                                        where s.s_usn = '{}' and (b2.lcard is null or b2.return_status = 'Returned'));'''.format(s_usn, s_usn))
        student_usns = [student.s_usn for student in Student.objects.raw("select s_usn from student") ]
        
        count = len(borrow)
        if s_usn in student_usns:
            if count == 0 or count == 1:
                return render(request, "library/canborrow.html", {'usn':s_usn, 'free':free})
            else:
                return render(request, "library/Cannotborrow.html", {'usn':s_usn, 'borrow':borrow})
        else: 
            return render(request, "library/errors/doesnotexist.html", {'usn':s_usn})

    return render(request, "library/check.html")

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
        return redirect('borrow')

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
        return redirect('borrow')

    return render(request, "library/addborjm.html")

def updborrow(request):
    result = None
    if request.method == 'POST':
        form = Inputform(request.POST)
        if form.is_valid():
            s_usn = form.cleaned_data['s_usn']
            try:
                student = Student.objects.get(s_usn = s_usn)
                not_returned = BorrowInfo.objects.filter(s_usn = student, return_status = 'Not Returned')
                result = not_returned
            except Student.DoesNotExist:
                result = "No student found with this USN..."
        elif 'return_book' in request.POST:
            trans_id = request.POST.get('trans_id')
            book = get_object_or_404(BorrowInfo, trans_id=trans_id)
            book.return_status = 'Returned'
            book.save()
            return redirect(reverse('updborrow'))
    else:
        form = Inputform()
        

    return render(request, "library/updborrow.html", {'form': form, 'result':result})

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

