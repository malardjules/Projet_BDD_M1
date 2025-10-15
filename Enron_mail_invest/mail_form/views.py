from django.shortcuts import render
from django.db import connection
from .forms import Form1,Form2,Form3,Form4,Form5,Form6,Form7
import matplotlib.pyplot as plt


def format_employee(rows):
    formatted_results = []
    for row in rows:
        employee_id, firstname, lastname, category, email = row[:5]
        
        if not category:
            category = "Non renseigné"

        for result in formatted_results:
            if result['employee_id'] == employee_id:
                result['emails'].append(email)
                break
            
        else:
            formatted_results.append({
                'employee_id': employee_id,
                'category': category,
                'emails': [email],
                'firstname': firstname,
                'lastname': lastname,
            })

    return formatted_results


def query1(request):
    if request.method == 'POST':
        form = Form1(request.POST)
        if form.is_valid():
            option = form.cleaned_data.get('option')
            if option == 'lastname':
                champ = form.cleaned_data['fields_lastname']
                query = f"""
                SELECT e.id, e.firstname, e.lastname, e.category, m.address 
                FROM mail_form_employee e JOIN mail_form_mailbox m ON e.id = m.employee_id 
                WHERE e.lastname ='{champ}';
                """
            else:
                champ = form.cleaned_data['fields_email']
                query = f"""
                SELECT e.id, e.firstname, e.lastname, e.category, m.address 
                FROM mail_form_employee e JOIN mail_form_mailbox m ON e.id = m.employee_id 
                WHERE e.id IN ( SELECT m.employee_id FROM mail_form_mailbox m WHERE m.address = '{champ}');
                """
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    results = format_employee(rows)
                    res=True
                except:
                    res=False
                    
            if res:
                return render(request, 'result.html', {'form': form, 'results': results})

    form = Form1()
    return render(request, 'Formulaire1.html', {'form': form})



def query2(request):
    if request.method == 'POST':
        form = Form2(request.POST)
        
        if form.is_valid():
            mail_type = form.cleaned_data['mailType']
            mail_count_comparison = form.cleaned_data['mailCountComparison']
            mail_count = form.cleaned_data['mailCount']
            start_date = form.cleaned_data['startDate']
            end_date = form.cleaned_data['endDate']
            exchange_type = form.cleaned_data['exchangeType']
            
            comparaison='>' if mail_count_comparison =='more' else '<'
            internal1='AND m_to.is_internal = TRUE' if exchange_type == 'internal' else ''
            internal2='AND m_from.is_internal = TRUE' if exchange_type == 'internal' else ''
            
            if mail_type =='sent':
                condition=f"""
                SELECT COUNT(DISTINCT mm.message_id)
                FROM mail_form_mailbox m
                INNER JOIN mail_form_mail mm ON mm.sender_id = m.address
                INNER JOIN mail_form_mail_to mt ON mm.message_id = mt.mail_id
                INNER JOIN mail_form_mailbox m_to ON mt.mailbox_id = m_to.address
                WHERE m.employee_id = e.id
                {internal1}
                AND mm.date BETWEEN '{start_date}' AND '{end_date}'
                """
            elif mail_type =='received':
                condition=f"""
                SELECT 
                COUNT(DISTINCT mm.message_id)
                FROM mail_form_mailbox m
                INNER JOIN mail_form_mail_to t ON t.mailbox_id = m.address
                INNER JOIN mail_form_mail mm ON mm.message_id = t.mail_id
                INNER JOIN mail_form_mailbox m_from ON mm.sender_id=m_from.address
                WHERE m.employee_id = e.id
                {internal2}
                AND mm.date BETWEEN '{start_date}' AND '{end_date}'
                """
            else:
                condition =f"""
                (SELECT COUNT(DISTINCT mm.message_id)
                 FROM mail_form_mailbox m
                 INNER JOIN mail_form_mail_to t ON t.mailbox_id = m.address
                 INNER JOIN mail_form_mail mm ON mm.message_id = t.mail_id
                 INNER JOIN mail_form_mailbox m_from ON mm.sender_id=m_from.address
                 WHERE m.employee_id = e.id
                 {internal2}
                 AND mm.date BETWEEN '{start_date}' AND '{end_date}'
                 )+
                (SELECT COUNT(DISTINCT mm.message_id)
                 FROM mail_form_mailbox m
                 INNER JOIN mail_form_mail mm ON mm.sender_id = m.address
                 INNER JOIN mail_form_mail_to mt ON mm.message_id = mt.mail_id
                 INNER JOIN mail_form_mailbox m_to ON mt.mailbox_id = m_to.address
                 WHERE m.employee_id = e.id
                 {internal1}
                 AND mm.date BETWEEN '{start_date}' AND '{end_date}'
                 )
                """   
            query = f"""
            SELECT e.id, e.firstname, e.lastname, e.category, mb.address
            FROM mail_form_employee e INNER JOIN mail_form_mailbox mb ON e.id=mb.employee_id
            WHERE ({condition}) {comparaison} {mail_count};
            """
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    results = format_employee(rows)
                    res=True
                except:
                    res=False
                    
            if res:
                return render(request, 'result.html', {'form': form, 'results': results})

    form = Form2()
    return render(request, 'Formulaire2.html', {'form': form})


def query3(request):
    if request.method == 'POST':
        form = Form3(request.POST)
        
        if form.is_valid():
            id_employee = form.cleaned_data['employeeID']
            start_date = form.cleaned_data['startDate']
            end_date = form.cleaned_data['endDate']

            query = f"""
            SELECT e.id, e.firstname, e.lastname, e.category, mbox.address
            FROM mail_form_mail m
            INNER JOIN mail_form_mailbox mb_sender ON mb_sender.address = m.sender_id
            INNER JOIN mail_form_mail_to t ON t.mail_id = m.message_id
            INNER JOIN mail_form_mailbox mb_to ON t.mailbox_id = mb_to.address
            INNER JOIN mail_form_employee e_sender ON mb_sender.employee_id = e_sender.id 
            INNER JOIN mail_form_employee e_to ON mb_to.employee_id = e_to.id
            INNER JOIN mail_form_employee e ON (e.id = e_to.id OR e.id = e_sender.id )AND e.id != {id_employee}
            INNER JOIN mail_form_mailbox mbox ON mbox.employee_id = e.id
            WHERE (e_sender.id ={id_employee} OR e_to.id ={id_employee}) AND m.date  BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY e.id,mbox.address;
            """
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    results = format_employee(rows)
                    res=True
                except:
                    res=False
                    
            if res:
                return render(request, 'result.html', {'form': form, 'results': results})

    form = Form3()
    return render(request, 'Formulaire3.html', {'form': form})


def format_couple_employee(rows):
    formatted_results = []
    c=1
    for row in rows:
        employee_id1, firstname1, lastname1, category1, employee_id2, firstname2, lastname2, category2, mail_count = row[:9]
        
        if not category1:
            category1 = "Non renseigné"
        if not category2:
            category2 = "Non renseigné"

        
        formatted_results.append({
            'employee_id1': employee_id1,
            'category1': category1,
            'firstname1': firstname1,
            'lastname1': lastname1,
            'employee_id2': employee_id2,
            'category2': category2,
            'firstname2': firstname2,
            'lastname2': lastname2,
            'mail_count': mail_count,
            'count': c
        })
        c+=1
    return formatted_results


def query4(request):
    if request.method == 'POST':
        form = Form4(request.POST)
        
        if form.is_valid():
            limit = form.cleaned_data['limitResult']
            start_date = form.cleaned_data['startDate']
            end_date = form.cleaned_data['endDate']

            query = f"""
            SELECT e1.id, e1.firstname, e1.lastname, e1.category, e2.id, e2.firstname , e2.lastname , e2.category, pairs.mail_count
            FROM (
            SELECT DISTINCT LEAST(mb_sender.employee_id, mb_to.employee_id) AS id_1, GREATEST(mb_sender.employee_id, mb_to.employee_id) AS id_2, COUNT(m.message_id) AS mail_count
            FROM mail_form_mail m
            INNER JOIN  mail_form_mailbox mb_sender ON mb_sender.address = m.sender_id
            INNER JOIN mail_form_mail_to t ON t.mail_id = m.message_id
            INNER JOIN mail_form_mailbox mb_to ON t.mailbox_id = mb_to.address
            WHERE m.date BETWEEN '{start_date}' AND '{end_date}' AND mb_sender.employee_id IS NOT NULL AND mb_to.employee_id IS NOT NULL
            GROUP BY id_1, id_2
            ) AS pairs
            INNER JOIN mail_form_employee e1 ON pairs.id_1 = e1.id
            INNER JOIN mail_form_employee e2 ON pairs.id_2 = e2.id
            ORDER BY pairs.mail_count DESC
            LIMIT  {limit};
            """
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    results = format_couple_employee(rows)
                    res=True
                except:
                    res=False
                    
            if res:
                return render(request, 'result2.html', {'form': form, 'results': results})

    form = Form4()
    return render(request, 'Formulaire4.html', {'form': form})



def query5(request):
    if request.method == 'POST':
        form = Form5(request.POST)
        
        if form.is_valid():
            start_date = form.cleaned_data['startDate']
            end_date = form.cleaned_data['endDate']
            exchange_type = form.cleaned_data['exchangeType']
            
            print(start_date,end_date,exchange_type)
            if exchange_type =='internal':
                internal="AND"
            else:
                internal="OR"
            query = f"""
            SELECT DATE(m.date), COUNT(*) 
            FROM mail_form_mail m
            WHERE date BETWEEN '{start_date}' AND '{end_date}'
            AND m.message_id IN (
                SELECT  mm.message_id 
                FROM mail_form_mail  mm 
                INNER JOIN mail_form_mailbox mb_sender ON mb_sender.address = mm.sender_id
                INNER JOIN mail_form_mail_to t ON t.mail_id = mm.message_id
                INNER JOIN  mail_form_mailbox mb_to ON t.mailbox_id = mb_to.address
                WHERE (mb_sender.is_internal =TRUE {internal} mb_to.is_internal = TRUE)
                )
            GROUP BY DATE(date)
            ORDER BY COUNT(*) DESC;
            """
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    results = []
                    date_count_dict = {} 
                    for row in rows:
                        date, count = row[:2]
                        results.append({
                            'date': date,
                            'count': count})
                        date_count_dict[date] = count
                    sorted_dates = sorted(date_count_dict.keys())
                    sorted_counts = [date_count_dict[date] for date in sorted_dates]
                    plt.figure(figsize=(10, 6))
                    plt.plot(sorted_dates, sorted_counts)
                    plt.title('Nombre de Mails Echangés par Jour')
                    plt.xlabel('Date')
                    plt.ylabel('Nombre de Mails')

                    plt.savefig('./static/graph.png')
                    res=True
                except:
                    res=False
            if res:
                return render(request, 'result3.html', {'form': form, 'results': results})

    form = Form2()
    return render(request, 'Formulaire5.html', {'form': form})



def format_emails(rows):
    formatted_results = []
    for row in rows:
        message_id, subject, sender_id, mailbox_id, content,date = row
        
        if not subject:
            subject = ""
        if not content:
            content = ""
        if not date:
            date = "inconue"
        for result in formatted_results:
            if result['message_id'] == message_id:
                print(mailbox_id)
                result['mailbox_ids'].append(mailbox_id)
                break


        else:
            print(message_id)
            print(subject)
            print(sender_id)
            formatted_results.append({
                'message_id': message_id,
                'subject': subject,
                'sender_id': sender_id,
                'mailbox_ids': [mailbox_id] if mailbox_id else [],
                'content': content,
                'date':date,
            })

    return formatted_results

def query6(request):
    if request.method == 'POST':
        form = Form6(request.POST)
        if form.is_valid():
            keywords = form.cleaned_data['keywords']
            sorttype = form.cleaned_data['sortType']
            
            if sorttype == 'sender':
                sort = "ORDER BY m.sender_id" 
            elif sorttype == 'subject':
                sort ="ORDER BY m.subject" 
            else:
                sort ="ORDER BY m.date"
            
            word_join = ""
            word_cond = ""
            i = 1
            for word in keywords:
                word_join += f" INNER JOIN mail_form_mail_word mw{i} ON mw{i}.mail_id = m.message_id "
                word_cond += f" AND mw{i}.word_id = '{word}' "
                i += 1
            query = f"""
            SELECT m.message_id, m.subject, m.sender_id, t.mailbox_id, m.content, m.date
            FROM mail_form_mail m
            LEFT JOIN mail_form_mail_to t ON m.message_id = t.mail_id
            {word_join}
            WHERE 1=1 {word_cond}
            {sort};
            """
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    results = format_emails(rows)
                    res=True
                except:
                    res=False
            if res:
                return render(request, 'result4.html', {'form': form, 'results': results})
    form = Form6()
    return render(request, 'Formulaire6.html', {'form': form})


def format_conversation(rows):
    formatted_results = []
    for row in rows:
        subject, email = row
        

        for result in formatted_results:
            if result['subject'] == subject:
                result['emails'].append(email)
                break
            
        else:
            formatted_results.append({
                'subject': subject,
                'emails': [email],
            })

    return formatted_results

def query7(request):
    if request.method == 'POST':
        form = Form7(request.POST)
        if form.is_valid():
            option = form.cleaned_data.get('option')
            if option == 'id':
                print("id")
                champ = form.cleaned_data['fields_id']
                query = f"""
                SELECT c.subject, cp2.mailbox_id
                FROM mail_form_conversation c 
                INNER JOIN mail_form_conversation_participants cp ON cp.conversation_id=c.subject
                INNER JOIN mail_form_mailbox mb ON mb.address = cp.mailbox_id
                INNER JOIN mail_form_employee e ON mb.employee_id = e.id
                INNER JOIN mail_form_conversation_participants cp2 ON cp2.conversation_id=c.subject
                WHERE e.id={champ};
                """
            else:
                print("email")
                champ = form.cleaned_data['fields_email']
                query = f"""
                SELECT c.subject, cp2.mailbox_id
                FROM mail_form_conversation c 
                INNER JOIN mail_form_conversation_participants cp ON cp.conversation_id=c.subject
                INNER JOIN mail_form_mailbox mb ON mb.address = cp.mailbox_id
                INNER JOIN mail_form_conversation_participants cp2 ON cp2.conversation_id=c.subject
                WHERE mb.address = '{champ}';
                """
            with connection.cursor() as cursor:
                try:
                    print("try")
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    results = format_conversation(rows)
                    for result in results:
                        print(result["subject"])
                    res=True
                except:
                    print("except")
                    res=False
                    
            if res:
                return render(request, 'result5.html', {'form': form, 'results': results})

    form = Form7()
    return render(request, 'Formulaire7.html', {'form': form})



def queryresult7(request):
    subject = request.GET.get('subject').replace("'", "''")
    query=f"""
    SELECT m.message_id, m.subject, m.sender_id, t.mailbox_id, m.content, m.date
    FROM mail_form_mail m
    INNER JOIN mail_form_conversation c ON c.subject=m.conversation_id
    INNER JOIN mail_form_mail_to t ON t.mail_id=m.message_id
    WHERE  c.subject='{subject}'
    """
    with connection.cursor() as cursor:
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            results = format_emails(rows)
            res=True
        except:
            res=False
    if res:
        return render(request, 'result4.html', { 'results': results})
    
    form = Form7()
    return render(request, 'Formulaire7.html', {'form': form})




def home(request):
    return render(request, 'home.html')

def format_request(rep,des):
    noms_colonnes = [col[0] for col in des]
    resultats_formates = []
    for resultat in rep:
        resultats_formates.append(dict(zip(noms_colonnes, resultat)))
    return resultats_formates

def requete(request):
    if request.method == 'POST':
        requete = request.POST.get('requete', '')
        with connection.cursor() as cursor:
            try:
                cursor.execute(requete)
                rep = cursor.fetchall()
                result=format_request(rep,cursor.description)
                res=True
            except:
                res=False
        
        if res:
            return render(request, 'requete.html', {'resultats': result})

    return render(request, 'requete.html')



