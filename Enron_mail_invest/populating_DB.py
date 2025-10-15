#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
    infos :
            -A terme, l'algorithme de détection des conversations en tant que réponses devrait être amélioré afin que deux conversations distinctes 
            ayant des sujets identiques ne soient pas considérées comme une seule et même conversation. Il convient de noter que l'absence
            du Message-ID des mails initiaux dans les réponses rend cette tâche complexe.
            
            -La durée d'exécution du script sur l'ensemble des données peut durer quelques heures
"""
           
import os
import sys
import django
import xml.etree.ElementTree as ET
import re
from os import walk
from dateutil import parser
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Enron_mail_invest.settings')
django.setup()

from mail_form.models import Employee, Mailbox, Mail, Word, Conversation


def log_error(message): #enregistre les erreurs rencontré lors de l'éxécution du script dans le fichier erreur.txt
    with open('erreur.txt', 'a') as error_file:
        error_file.write(message + '\n')


def fill_employee_and_mailbox(XML_file): #remplissage du fichier XML
    tree = ET.parse(XML_file)
    root = tree.getroot()
    
    for employee in root.findall('employee'):
        category = employee.get('category')
        lastname = employee.find('lastname').text
        firstname = employee.find('firstname').text
        email_addresses = [email.get('address') for email in employee.findall('email')]
        print(lastname)
        try:
            employ=Employee.objects.create(category=category, lastname=lastname, firstname=firstname)
        except Exception as e:
            error_message = f"Erreur lors de la création d'une mailbox: {e}\n{traceback.format_exc()}"
            log_error(error_message)
            print(error_message)
            continue
        
        for email in email_addresses:
            try:
                mailbox, created = Mailbox.objects.get_or_create(address=email)
                mailbox.employee = employ
                if "enron" in email.lower() and created :
                    mailbox.is_internal = True
                mailbox.save()
            except Exception as e:
                error_message = f"Erreur lors de la création d'une mailbox: {e}"
                log_error(error_message)
                print(error_message)
                continue
            
    print("les tables liés au fichier XML ont bien été remplis")
    
    
def comp_regex(): #permet de compliler une seule fois toutes les regex 
    reg_id=re.compile(r'^\s*Message-ID: (.+)',re.MULTILINE)
    reg_date=re.compile(r'^\s*Date: (.+)',re.MULTILINE)
    reg_from=re.compile(r'^\s*From: (.+)',re.MULTILINE)
    reg_to=re.compile(r'^\s*To:\s*(([^,\s]+@[^,\s]+\s*,?\s*)*)',re.MULTILINE)
    reg_cc=re.compile(r'^\s*Cc:\s*(([^,\s]+@[^,\s]+\s*,?\s*)*)',re.MULTILINE)
    reg_bcc=re.compile(r'^\s*Bcc:\s*(([^,\s]+@[^,\s]+\s*,?\s*)*)',re.MULTILINE)
    reg_suj=re.compile(r'^\s*Subject: (.+)',re.MULTILINE)
    reg_entete=re.compile(r'^(.*?)\n\n(.*)$',re.DOTALL)
    reg_word=re.compile(r'\b\w+|\W(?<=-)\b')
    reg_conv=re.compile(r'R[eE]:\s*(.*)')
    
    return {
        "id": reg_id,
        "date": reg_date,
        "from": reg_from,
        "to": reg_to,
        "cc": reg_cc,
        "bcc": reg_bcc,
        "subject": reg_suj,
        "entete": reg_entete,
        "word": reg_word,
        "conv": reg_conv
    }
     
  
def parse_file(file,regex):  #Prend un entree un fichier représentant un mail et ses metadonnées, ainsi que les regex à capturer et retourne les informations utilises.
    with open(file, 'r',errors='ignore') as file:
        email_file = file.read()
    
    res = regex["entete"].match(email_file)
    entete=res.group(1)
    corps=res.group(2)
    
    id_reg = regex["id"].search(entete)
    date_reg = regex["date"].search(entete)
    from_reg = regex["from"].search(entete) 
    to_reg = regex["to"].search(entete) 
    cc_reg = regex["cc"].search(entete)
    bcc_reg = regex["bcc"].search(entete)
    subject_reg= regex["subject"].search(entete)

    from_email = from_reg.group(1) if from_reg else None
    id_email = id_reg.group(1) if id_reg else None
    to_email = [email.strip() for email in to_reg.group(1).split(',')] if to_reg else None
    cc_email = [email.strip() for email in cc_reg.group(1).split(',')] if cc_reg else None
    bcc_email = [email.strip() for email in bcc_reg.group(1).split(',')] if bcc_reg else None
    date_email = date_reg.group(1) if date_reg else None
    subject_email = subject_reg.group(1) if subject_reg else None
    content_email = corps if corps else None
    
    return {
        "id": id_email,
        "date": date_email,
        "from": from_email,
        "to": to_email,
        "cc": cc_email,
        "bcc": bcc_email,
        "subject": subject_email,
        "content": content_email,
        "word": regex["word"].findall(content_email)
    }


def add_conv(mail,data,conv_reg): #gere l'ajout et la création de conversations 
    suj=data["subject"]
    rep= conv_reg.match(suj)
    if not rep:
        try:
            Convers = Conversation.objects.get(suj)
        except:
            return
    else:
        s=rep.group(1)
        Convers, created = Conversation.objects.get_or_create(subject=s)
    if created:
        try:
            mailConv = Mail.objects.get(subject=s) #vérifie si on a pas déja rentré un mail avec ce sujet (pour l'ajouter aussi à la conv)
            mailConv.conversation=Convers
            send=mailConv.sender
            Convers.participants.add(send)
        except:
            pass
        
    mail.conversation=Convers
    Convers.participants.add(data["from"]) 
    if data["to"]: 
        add_mailboxs(data["to"], Convers.participants) #ajoute les destinataires directes (to)
    Convers.save()
   
    
def add_mailboxs(mails,dest): #gere l'ajout et la création de destinataires (to,cc,bcc)
    existing_mailboxes = Mailbox.objects.filter(address__in=mails)
    existing_mailbox_set = set(mb.address for mb in existing_mailboxes)
    new_mailboxes = []
    mailboxes_added = set()
    
    for email in mails:
        if email not in mailboxes_added:
            if email not in existing_mailbox_set:
                newmail=Mailbox(address=email)
                if "enron" in email.lower() :
                    newmail.is_internal=True
                new_mailboxes.append(newmail)
            mailboxes_added.add(email)

    if new_mailboxes:
        Mailbox.objects.bulk_create(new_mailboxes)

    dest.add(*existing_mailboxes)
    dest.add(*new_mailboxes)
    
    
def add_words(words,word_atr): #gere l'ajout et la création de mots
    existing_words = Word.objects.filter(word__in=words)
    existing_word_set = set(w.word for w in existing_words)
    new_words = []
    words_added = set()
    
    for word in words:
        if word not in words_added:
            if word not in existing_word_set:
                new_words.append(Word(word=word))
            words_added.add(word)
            
    if new_words:
        Word.objects.bulk_create(new_words) #requete groupé pour les performances
        
    word_atr.add(*existing_words)
    word_atr.add(*new_words)
    
    
def add_data(chemin_complet,data,conv_reg):  #prend un dictionnaire contenant les informations importantes et les ajoutes à la base de donnée 
    mailbox, created = Mailbox.objects.get_or_create(address=data["from"])
    if "enron" in data["from"].lower() and created :
        mailbox.is_internal = True
        mailbox.save()
        
    mail=Mail.objects.create(  
        message_id =data["id"],
        sender=mailbox,
        date=parser.parse(data["date"]),
        subject=data["subject"],
        content=data["content"],
        file=chemin_complet)
    
    if data["subject"]:
        add_conv(mail, data,conv_reg)  #ajoute les conversations (identifier par Re dans le sujet)
        
    if data["to"]: 
        add_mailboxs(data["to"], mail.to)  #ajoute les destinataires directes (to)
        
    if data["cc"]:
        add_mailboxs(data["cc"], mail.cc)  #ajoute les destinataires indirectes (cc)
        
    if data["bcc"]:
        add_mailboxs(data["bcc"], mail.bcc)  #ajoute les destinataires indirectes (bcc)
        
    if data["word"]:
        add_words(data["word"],mail.word)  #ajoute les mots
        
    mail.save()
    
    
def fill_mails(directory):  #Fonction de remplissage du repertoire de mails dans la base de donnée
    regex=comp_regex()# On compile les regex
    
    for (repertoire, sousRepertoires, fichiers) in walk(directory):
        for fichier in fichiers:  #On parcours les fichiers du repertoire
            chemin_complet = os.path.join(repertoire, fichier)
            print(chemin_complet)
            data=parse_file(chemin_complet,regex)  #On récupere les informations importantes du fichier
            try:     
                add_data(chemin_complet, data,regex["conv"])  #On remplis la base de donnée
            except Exception as e:
                error_message = f"{chemin_complet}:\n\n Erreur lors de la création d'une mailbox: {e}\n{traceback.format_exc()}\n\n"
                log_error(error_message)
                print(error_message)
                continue
    print("Les tables liés aux mails ont bien été remplis")
    
    
def sort_args(arg): #tri les arguments 
    XML_file=None
    directory=None
    if len(arg) >1:
        file = os.path.expanduser(arg[1])
        if file.endswith('.xml'):
            XML_file=file
            if len(arg) >2:
                directory=os.path.expanduser(arg[2])
        else:
            directory=file
            if len(arg) >2:
                XML_file=os.path.expanduser(arg[2])
    else:
        print("Entrez le fichier xml et/ou le répertoire contenant les mails en argument ")
    return XML_file,directory
    
    
if __name__ == "__main__": # prend le répertoire et/ou le fichier XML en parametres dans n'importe quel ordre et remplis la base de donnée 
    XML_file, directory = sort_args(sys.argv) #tri les arguments 
    
    if XML_file:
        fill_employee_and_mailbox(XML_file) #peuplement du fichier xml
    if directory:
        fill_mails(directory) #peuplement du répertoire
            
        