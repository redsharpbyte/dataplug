from arango import ArangoClient
# import arango.exceptions as ohoh


class Client():

    def __init__(self, db_config={}):
        """Initiate the connection keeper

            Arango databases are referred as domains
            Arango collections are referred as collections
        """
        # Local and object initializations
        self.is_connected = True
        self._domain = None
        self._collection = None

        # Check client info to the Arango Database
        db_config = self.check_credentials(db_config)

        # Database server connection
        try:
            self.client = ArangoClient(
                protocol=db_config['protocol'],
                host=db_config['host'],
                port=db_config['port'],
                username=db_config['username'],
                password=db_config['password'])
        except Exception as eee:
            self.is_connected = False

        # Checking connection success
        if self.is_connected:

            try:
                self.is_connected = self.client.verify()
            except Exception as eee:
                self.is_connected = False

            if self.is_connected and "domain" in db_config:
                self.domain = db_config["domain"]
                if "collection" in db_config:
                    self.collection = db_config["collection"]

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, domain_name):
        """ Sets the current domain object

            If the domain name has already been used then the domain is
            reloaded from the database else it is created if non-existent.
        """
        if domain_name not in self.client.databases():
            self._domain = self.client.create_database(domain_name)
        else:
            self._domain = self.client.database(domain_name)
        return self._domain

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, collection_name):
        if self._domain:
            if self._collection:
                if collection_name == self._collection.name:
                    return self._collection

            if collection_name in map(lambda c: c['name'], self._domain.collections()):
                self._collection = self._domain.collection(collection_name)
            else:
                self._collection = self._domain.create_collection(collection_name)
        return self._collection

    def check_credentials(self, db_config):
        """Fill missing fields with default values
        """
        if "protocol" not in db_config:
            db_config["protocol"] = "https"
        if "host" not in db_config:
            db_config["host"] = "localhost"
        if "port" not in db_config:
            db_config["port"] = 8529
        if "username" not in db_config:
            db_config["username"] = ""
        if "password" not in db_config:
            db_config["password"] = ""
        return db_config

    def collect(self, domain_name, collection_name):
        """ Set a new collection and domain at the same time """
        self.domain = domain_name
        self.collection = collection_name
        return self._collection

    def delete_collection(self):
        """ Delete the current collection

            return as arango.database.Database().delete_collection()

        """
        if self._domain is None or self._collection is None:
            return False
        try:
            self._collection.unload()
        except Exception as eee:
            pass
        return self._domain.delete_collection(self._collection.name, ignore_missing=True)

    def all(self, limit=None, only_fields=["_id"]):
        """ Return a list of this object
            This transforms the cursor list into a python list

            :param limit: limit the number of objects returned
            :param only_fields: fields key to be selected
                                in the returned objects
        """
        listing = []

        # --- Just select all documents in this collection
        cursor = self.collection.all(limit=limit)
        if cursor.count() > 0:
            listing = cursor.batch()
            for L in listing:
                for x in [field not in only_fields for field in L]:
                    L.pop(x)

        return listing

    def get(self, key=""):
        """ Return the data of the node/document with given key

            :param key: key part of the full id "collection_name/key"
                       because used on the collection object already.
        """
        info = {}

        if key == "":
            key = self.key()

        if key == "":
            return info

        try:
            info = self.collection.get(str(key))
            if info is None:
                info = {}
        # except ohoh.DocumentRevisionError as eee:
        # except ohoh.DocumentGetError as eee:
        except Exception as eee:
            info = {}

        return info

    def delete(self, key=""):
        """ Delete the node/document with given key, from current collection

            :param key: key of the championship, else the current data is used
            :return: a boolean representing the deletion status
        """
        if self._domain is None or self._collection is None:
            return False

        rinfo = False

        if key == "":
            return rinfo

        try:
            rinfo = self.collection.delete(str(key))
        except Exception as eee:
            rinfo = False

        return rinfo

    def find(self, sdict):
        """ Simple search that returns the dict for the found object information

            :param sdict: search dictionnary
            :return: the dictionary of the found data
        """
        info = {}

        if self._domain is None or self._collection is None or sdict == {}:
            return info

        try:
            cur = self.collection.find(sdict)
            if cur.count() == 1:
                info = cur.next()
            else:
                info = {}
        except Exception as eee:
            info = {}

        return info
