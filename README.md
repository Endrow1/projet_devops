# Projet DevOps - Infrastructure Multi-Machines & Déploiement Automatisé (Flask & MySQL)


## Architecture Spécifiée & Réseau

L'infrastructure réseau est segmentée au sein d'un VPC dédié afin de cloisonner hermétiquement les couches applicatives et de données conformément aux exigences de sécurité.

* **Point d'entrée unique (Load Balancer) :** Un AWS Application Load Balancer (ALB) public reçoit tout le trafic Internet. Il expose l'application sur le port HTTP (80) et le port sécurisé HTTPS (443). Le chiffrement SSL/TLS est configuré directement sur l'ALB via un certificat auto-signé importé dans AWS IAM.
* **Instances Applicatives (Haute Disponibilité) :** 2 instances EC2 identiques (Ubuntu 24.04 Noble) hébergent l'application Flask. Elles sont réparties de manière redondante sur deux zones de disponibilité distinctes (eu-west-3a et eu-west-3b) et reçoivent le trafic filtré de l'ALB.
* **Base de données isolée :** Une instance managée AWS RDS MySQL 8.0 stocke les données d'application. Elle est positionnée dans des sous-réseaux privés et isolés du Web.
* **Espace de Sauvegarde :** Un bucket AWS S3 sécurisé est provisionné pour accueillir les archives de sauvegardes automatiques de la base de données.

### Flux Réseau & Ports

* **`lb_sg`** (AWS ALB) -> Écoute ports HTTP (80) et HTTPS (443) depuis `0.0.0.0/0` (Internet).
* **`app_sg`** (EC2 Apps) -> Écoute port SSH (22) depuis `0.0.0.0/0` (Administration / CI/CD).
* **`app_sg`** (EC2 Apps) -> Écoute port Flask (5000) depuis le groupe de sécurité `lb_sg` uniquement.
* **`db_sg`** (AWS RDS) -> Écoute port MySQL (3306) depuis le groupe de sécurité `app_sg` uniquement.

---

## Stratégie de Sauvegarde & Restauration (Disaster Recovery)

### 1. Sauvegarde Automatisée (Backup)
Le rôle Ansible `backup` configure une tâche planifiée  sur le serveur de production :
* **Script de Backup :** Un template Bash `backup.sh.j2` est déployé. Il exécute une commande `mysqldump` pour AWS RDS (en incluant les options `--set-gtid-purged=OFF` et `--column-statistics=0` afin de garantir la compatibilité sans exiger de privilèges `SUPER`).
* **Planification (Cron) :** Le script est exécuté automatiquement **toutes les minutes**.
  * *Justification :* Cette fréquence a été choisie pour le cadre de l'évaluation du TP afin de constater la création immédiate d'archives dans le bucket S3, sans devoir patienter 24 heures. Dans un cadre de production réel, une récurrence quotidienne hors des heures de pointe serait privilégiée.
* **Exécution unique (`run_once: true`) :** Afin d'éviter les écritures concurrentes et les conflits de fichiers sur le bucket S3, Ansible configure le Cron de sauvegarde sur **une seule instance applicative** de l'inventaire.

### 2. Procédure de Restauration rapide
pour cloner la base de données, un playbook indépendant `restore.yml` permet de restaurer la dernière sauvegarde disponible sur S3 en une seule commande :

ansible-playbook -i ansible/inventory.ini ansible/restore.yml

**Actions automatisées par le playbook de restauration :**
1. Connexion SSH à la machine applicative principale.
2. Interrogation et téléchargement du dernier dump `.sql` disponible depuis le bucket S3 via l'AWS CLI.
3. Injection directe des structures et des données dans l'instance privée AWS RDS MySQL.
4. Suppression sécurisée du fichier SQL temporaire sur le disque local de la VM.

---

## Guide de Déploiement (Étape par étape)

### Prérequis système
* Terraform installé localement.
* Ansible installé localement.
* Vos identifiants de connexion AWS (clés d'accès) configurés dans vos variables d'environnement.

### Étape 1 : Préparation des variables secrètes
Créez un fichier nommé `terraform.tfvars` à la racine du projet (ce fichier est déjà protégé et ignoré par Git via le `.gitignore`) :

db_password =  
ssh_private_key_path =  
ssh_public_key_path =  
aws_access_key_id =  
aws_secret_access_key =  

### Étape 2 : Provisionnement de l'Infrastructure Cloud
Initialisez les providers et déployez l'ensemble de l'architecture réseau et matérielle sur AWS :

terraform init
terraform apply -auto-approve

À la fin de son exécution, Terraform va automatiquement générer le fichier d'inventaire à jour `ansible/inventory.ini` en y injectant les adresses IP publiques de vos instances EC2 ainsi que les variables d'accès à la base de données RDS.

### Étape 3 : Configuration logicielle et Déploiement via Ansible
Lancez le playbook principal pour installer l'environnement d'exécution Flask sur vos serveurs et mettre en place la routine de backup :

ansible-playbook -i ansible/inventory.ini ansible/playbook.yml

### Étape 4 : Validation du fonctionnement HTTPS
1. Récupérez l'URL DNS publique de votre Application Load Balancer (fournie dans les outputs de Terraform).
2. Ouvrez votre navigateur et saisissez l'adresse sous la forme : `https://<VOTRE-DNS-ALB>`.
3. Le navigateur affichera un avertissement rouge **"Connexion non privée" / "Non sécurisé"** : **C'est le comportement attendu**. S'agissant d'un certificat SSL auto-signé généré dynamiquement par Terraform pour le TP, le navigateur ne connaît pas l'autorité de certification. Les données échangées sont néanmoins entièrement chiffrées de bout en bout (TLS/SSL).
4. En cliquant sur les détails du certificat, vous pourrez valider l'identité de l'émetteur : `Efrei Projet DevOps`.

---

## Gestion de la Sécurité & Secrets

* Le fichier `.gitignore` bloque en amont l'envoi des fichiers d'états locaux (`*.tfstate`, `*.tfstate.backup`), du fichier de définition des variables (`*.tfvars`) ainsi que du fichier d'inventaire temporaire généré localement (`inventory.ini`).
* Les clés privées et les mots de passe de production ne transitent jamais dans du code applicatif et ne sont pas sur git.