from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import mysql.connector as sql
from .models import Student, AdminInfo, BookInfo, OtherBooks, BorrowInfo
from .forms import *
from django.db import connection
s_usn = ''
spassword = ''
username = ''
password = ''
#login for students.
def student_login(request):
    global s_usn, spassword
    if request.method == "POST":
        d = request.POST
        for key, value in d.items():
            if key == "s_usn":
                s_usn = value
            if key == "spassword":
                spassword = value
        with connection.cursor() as cursor:
            cursor.execute("select count(*), student_name FROM library.student WHERE s_usn = %s AND spassword = %s", [s_usn, spassword])
            result = cursor.fetchone()
            if result[0] > 0:
                student_name = result[1]
                request.session['s_usn'] = s_usn
                return render(request, "library/student.html", {'student_name': student_name})
            else:
                return render(request, 'library/student_login.html', {'error': 'Invalid USN or password'})
    return render(request, 'library/stulogin.html') 


#login for admins
def admin_login(request):
    global username, password
    if request.method == "POST":
        m=sql.connect(host="localhost", user="root", passwd="chatterbox1", database="library")
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

def profile(request):
    s_usn = request.session.get('s_usn')
    with connection.cursor() as cursor:
        cursor.execute('''(select s.s_usn, s.student_name, s.branch, s.sem, b.trans_id, b.ob_id, b.b_id, b.issue_date, b.due_date, b.lcard
                       from library.student s
                       join library.borrow_info b ON s.s_usn = b.s_usn
                       where s.s_usn = '{}' and b.return_status <> 'Returned');'''.format(s_usn))
        rows = cursor.fetchall()
    detail = []
    for row in rows:
        detail.append({
            's_usn': row[0],
            'student_name': row[1],
            'branch':row[2],
            'sem':row[3],
            'trans_id':row[4],
            'ob_id' : row[5],
            'b_id': row[6],
            'issue_date':row[7],
            'due_date':row[8],
            'lcard' : row[9],   
        })
    return render(request, "library/profile.html", {'detail':detail, 's_usn':s_usn})

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
        borrow = BorrowInfo.objects.raw('''select trans_id, b.s_usn, b.return_status, b.lcard, b.due_date 
                from borrow_info b, student s 
                where b.s_usn = '{}' and  (s.s_usn = b.s_usn 
                and (b.lcard = s.Lib_card_no_1 and return_status = 'Not Returned')
                or (b.lcard = s.Lib_card_no_2 and return_status = 'Not Returned'));'''.format(s_usn))
        with connection.cursor() as cursor:
            cursor.execute('''(SELECT s.Lib_card_no_1 AS library_card, s.s_usn
                            FROM library.student s
                            WHERE s.s_usn = '{}'
                            AND NOT EXISTS (SELECT *
                                FROM library.borrow_info b1
                                WHERE b1.s_usn = s.s_usn
                                AND b1.lcard = s.Lib_card_no_1
                                AND b1.return_status <> 'Returned'
                            ))
                        UNION
                        (
                            SELECT s.Lib_card_no_2 AS library_card, s.s_usn
                            FROM library.student s
                            WHERE s.s_usn = '{}'
                            AND NOT EXISTS (
                                SELECT *
                                FROM library.borrow_info b2
                                WHERE b2.s_usn = s.s_usn
                                AND b2.lcard = s.Lib_card_no_2
                                AND b2.return_status <> 'Returned')
                        );'''.format(s_usn, s_usn))
            rows = cursor.fetchall()
        libcard = []
        for row in rows:
            libcard.append({
                'library_card': row[0],
                's_usn':row[1],
            })
        student_usns = [student.s_usn for student in Student.objects.raw("select s_usn from student") ]
            
        count = len(borrow)
        if s_usn in student_usns:
            if count == 0 or count == 1:
                return render(request, "library/canborrow.html", {'usn':s_usn, 'free':libcard})
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

def booksstu(request):
    books = BookInfo.objects.raw("(select  book_id, isbn, title, authors, rack_no, categoty from book_info) UNION (select ob_id, issn, title, authors, rack_no, category from other_books);")
    context = {
        'books': books
    }
    return render(request, "library/booksstu.html", context)

def trending(request):
    books = BorrowInfo.objects.raw('''(select trans_id, title, count(br.isbn_or_issn) as borrow_count 
                                  from borrow_info br 
                                  join book_info b on b.book_id = br.b_id 
                                 Group by b.title)
                                   union
                                   (select trans_id, title, count(br.isbn_or_issn) as borrow_count 
                                  from borrow_info br 
                                  join other_books o on o.ob_id = br.ob_id 
                                 Group by o.title)
                                   order by borrow_count desc
                                   limit 10''')
    context = {
        'books': books
    }
    return render(request, "library/complex/trending.html", context)

def pastdue(request):
    stu_pastdue = Student.objects.raw('''select s.student_name, s.s_usn,
                                        DATEDIFF(CURDATE(), bi.due_date) AS days_overdue,
                                        30 + ((DATEDIFF(CURDATE(), bi.due_date) - 30)*2) AS fine
                                        from library.student s
                                        join library.borrow_info bi ON s.s_usn = bi.s_usn
                                        WHERE bi.return_status = 'Not Returned'
                                            AND DATEDIFF(CURDATE(), bi.due_date) > 30;''')
    context = {
        'stu_pastdue':stu_pastdue
    }
    return render(request, "library/complex/pastdue.html", context)

def avail(request):
    with connection.cursor() as cursor:
        cursor.execute('''(SELECT b.isbn, b.title, COUNT(b.book_id) AS total_copies, 
                COUNT(CASE WHEN bi.return_status = 'Not Returned' THEN 1 END) AS borrowed_copies,
                (COUNT(b.book_id) - COUNT(CASE WHEN bi.return_status = 'Not Returned' THEN 1 END)) AS available_copies
                FROM library.book_info b
                LEFT JOIN library.borrow_info bi ON b.book_id = bi.b_id
                GROUP BY b.isbn, b.title)
                UNION
                (SELECT o.issn, o.title, COUNT(o.ob_id) AS total_copies, 
                COUNT(CASE WHEN bi.return_status = 'Not Returned' THEN 1 END) AS borrowed_copies,
                (COUNT(o.ob_id) - COUNT(CASE WHEN bi.return_status = 'Not Returned' THEN 1 END)) AS available_copies
                FROM library.other_books o
                LEFT JOIN library.borrow_info bi ON o.ob_id = bi.ob_id
                GROUP BY o.issn, o.title)
                order by title asc''')
        rows = cursor.fetchall()

    # Process the rows to get the list of books with their counts
    avail = []
    for row in rows:
        avail.append({
            'isbn': row[0],
            'title': row[1],
            'total_copies': row[2],
            'borrowed_copies': row[3],
            'available_copies': row[4]
        })

    return render(request, 'library/complex/availability.html', {'avail': avail})

def unused(request):
    with connection.cursor() as cursor:
        cursor.execute('''(SELECT distinct b.title, b.isbn
                                FROM library.book_info b
                                LEFT JOIN library.borrow_info bi ON b.book_id = bi.b_id
                                WHERE b.isbn NOT IN (
                                    SELECT b2.isbn
                                    FROM library.book_info b2
                                    JOIN library.borrow_info bi2 ON b2.book_id = bi2.b_id
                                    WHERE bi2.issue_date >= DATE_SUB(CURDATE(), INTERVAL 5 MONTH)
                                ))
                                UNION
                                (SELECT distinct o.title, o.issn
                                FROM library.other_books o
                                LEFT JOIN library.borrow_info bi ON o.ob_id = bi.ob_id
                                WHERE o.issn NOT IN (
                                    SELECT o2.issn
                                    FROM library.other_books o2
                                    JOIN library.borrow_info bi2 ON o2.ob_id = bi2.ob_id
                                    WHERE bi2.issue_date >= DATE_SUB(CURDATE(), INTERVAL 5 MONTH)));''')
        rows = cursor.fetchall()
    unused = []
    for row in rows:
        unused.append({
            'title': row[0],
            'isbn': row[1],
        })

    return render(request, "library/complex/unused.html", {'unused':unused})

def regular(request):
    with connection.cursor() as cursor:
        cursor.execute('''select s.student_name, s.s_usn, count(b.trans_id) as total_borrowed
                        from library.borrow_info b
                        join library.student s on s.s_usn = b.s_usn
                        group by s.s_usn, s.student_name
                        order by total_borrowed desc
                        limit 5;''')
        rows = cursor.fetchall()
    regular = []
    for row in rows:
        regular.append({
            'student_name': row[0],
            's_usn': row[1],
            'total_borrowed':row[2],
        })

    return render(request, "library/complex/regularbor.html", {'regular':regular})

