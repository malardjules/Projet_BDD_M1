# README - Application Web pour l'Analyse des Données de l'Affaire Enron

Cette application permet aux enquêteurs d'explorer, de visualiser et d'analyser les données issues des e-mails d'Enron en utilisant des requêtes paramétrées.

## Installation

Pour utiliser cette application localement, veuillez suivre les étapes suivantes:

1. Assurez-vous d'avoir Python et PostgreSQL installés sur votre système.

2. Clonez ce dépôt GitHub sur votre machine :
   ```bash
   git clone 
   ```
3. Installez les dépendances requises :
   ```bash
   pip install -r requirements.txt
   ```
4. Créez une base de données PostgreSQL et renseigner les informations requises dans le fichier `settings.py` dans le répertoire `Projet_BDD_M1/Enron_mail_invest/Enron_mail_invest/`:
   ```python
	   DATABASES = {
	      	"default": {
			"ENGINE": "django.db.backends.postgresql",
			"NAME": "nom_de_votre_DB",
			"USER": "votre_nom_utilisateur",
			"PASSWORD": "votre_mdp",
			"HOST": "localhost", 
			"PORT": "5432",  
		}
	   }
    ```

6. Creer les tables de la base de données:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

7. récupérer les données (fichier XML des employés et dossier contenant les mails):
   
   	[arborescence de boîtes mails](https://math.univ-angers.fr/perso/jaclin/enron/enron_mail_20150507.tar.gz) et 
   	[fichier XML](https://math.univ-angers.fr/perso/jaclin/enron/employes_enron.xml)
  

8. Exécutez le script de peuplement de la base de données :
   ```bash
   python populating.py chemin/vers/enron_mail_20150507 chemin/vers/employes_enron.xml
   ```

9. Lancez l'application:
   ```bash
   python manage.py runserver
   ```

---
*Ce projet a été développé par Jules Malard (https://github.com/Amugith) et Souheid Nasser Djama (https://github.com/Souheid) dans le cadre du module BDDR - M1 Data Science - Université d'Anger. Enseignants : Claudia A. Vasconcellos-Gaete et Jacquelin Charbonnel*  

