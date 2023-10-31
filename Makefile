SERVER_DIR='/var/www/friendsgiving/friendsgiving'

.PHONY: deps-local
deps-local:
	sudo apt update
	sudo apt install make
	pip3 install -r requirements.txt

.PHONY: run
run:
	python3 friendsgiving/api.py

.PHONY: deps-server
deps-server:
	sudo apt update
	sudo apt install -y apache2 libapache2-mod-wsgi python-dev python3-pip
	sudo ufw allow 'Apache'
	sudo systemctl status apache2
	pip3 install -r requirements.txt

.PHONY: build-server
build-server:
	sudo mkdir /var/www/friendsgiving
	cp -r ./friendsgiving /var/www/friendsgiving/
	mv $(SERVER_DIR)/api.py $(SERVER_DIR)/__init__.py
	cp server_files/friends_server.conf /etc/apache2/sites-available/
	cp server_files/friends_server.wsgi /var/www/friendsgiving/
	touch $(SERVER_DIR)/.env	
	echo "--- BUILD COMPLETE ---"
	echo "empty .env file placed @ $(SERVER_DIR)/.env"
	echo "this must be filled out with the appropriate environment variables to function"

