#
# This is a REST service that does a couple things. One thing that this service does is cleans and tidies data
# presented to it by its clients. These input data are expected to be encoded as a single JSON document containing a
# list of 'category => value' name-value pairs. The values can be arbitrary JSON data types however the categories
# (or keys) must be from a recognizable list. The other thing this service does does is maintain the canonical list of
# categories that are authoritative. Any data submitted to this web service that does not use one or more categories
# from this authoritative list will be elided them from the output entirely. The data submitted to this service is
# expected to be passed in the form of a JSON document and likewise a JSON document is returned that represents the
# simplified or "cleaned" version of the original.
#

__author__ = 'johnwswift@gmail.com'
__version__ = '1.0'

import httplib
from collections import OrderedDict
from flask import Flask, jsonify, abort, escape, make_response
from flask.ext.restful import reqparse, Api, Resource
from flask.ext.httpauth import HTTPBasicAuth

# The (default) global list of categories and their associated counters that we track in memory
category_db = OrderedDict()
category_db[u'PERSON'] = 0
category_db[u'PLACE'] = 0
category_db[u'ANIMAL'] = 0
category_db[u'COMPUTER'] = 0
category_db[u'OTHER'] = 0

# Secure this service using simple static HTTP Basic credentials
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    return 'ratswen' if username == 'newstar' else None

@auth.error_handler
def unauthorized():
    # Take some liberties with the HTTP response code to force browser user agents to
    # not display their default authentication dialog so an error message is displayed instead.
    return make_response(jsonify({'message': 'Unauthorized access'}), httplib.FORBIDDEN)


class Category(Resource):
    """ This service manages categories as its sole RESTful resource. This class provides a REST API
        that allows clients to effectively manage these resources.
    """
    decorators = [auth.login_required]

    def get(self, name):
        """ If a valid category name is requested, this will return the current count associated with
        that category which reflects how many times that category has been encountered so far by this service.
        """
        if name is not None:
            try:
                return {'count': category_db[escape(name.upper())]}
            except KeyError:
                pass

        abort(httplib.NOT_FOUND)

    def put(self, name):
        """ Inserts a category name into the global category database.
        """
        if name is not None:
            name = escape(name.upper())
            category_db[name] = 0
            return {u'message': u'Successfully added category ' + name}
        else:
            abort(httplib.BAD_REQUEST)

    def delete(self, name):
        """ Removes a category from the global category database.
        """
        if name is not None:
            name = escape(name.upper())
            try:
                del category_db[name]
                return {u'message': u'Successfully removed category ' + name}
            except KeyError:
                abort(httplib.NOT_FOUND)
        else:
            abort(httplib.BAD_REQUEST)


class Categories(Resource):
    """ This resource represents a list of categories managed by this service including their starting counts
    """
    decorators = [auth.login_required]

    def get(self):
        """ Returns the entire list of category/count pairs to the caller as a single JSON object document
        """
        return make_response(jsonify(category_db), httplib.OK)

    def post(self):
        """ Updates the entire category database with a single HTTP transaction
        """
        abort(httplib.NOT_IMPLEMENTED)


class Results:
    """ A concrete results abstraction that represents the final 'cleaned' results of a submission
        to this web service. It includes the list of valid category-subcategory pairs and the total
        counts of each valid category found in the original input.
    """
    def __init__(self):
        self.categories = []
        self.counts = {}

    def add(self, category, subcategory):
        if category is not None:
            category = category.upper()
            if category in category_db:
                # We have a legitimate category now check for dups
                entry = (category, subcategory)
                if entry not in self.categories:
                    # We have a unique entry so it's OK to add
                    self.categories.append(entry)

                    # Update our counts for this category as well
                    # both for this particular result and our db
                    if category in self.counts:
                        self.counts[category] += 1
                    else:
                        self.counts[category] = 1

                    category_db[category] += 1


class Cleaner(Resource):
    """ Our data cleaning web service. The incoming data is expected to be a list of category sub-category
        name-value pairs in the form of a JSON object with a single 'categories' array property. This is
        strictly enforced and any submission that does not meet this criteria will be rejected.
    """
    decorators = [auth.login_required]

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('categories', type=list, required=True, help='No categories given', location='json')
        super(Cleaner, self).__init__()

    def post(self):
        results = Results()
        args = self.parser.parse_args()
        for category in args['categories']:
            if isinstance(category, list) and len(category) >= 2:
                results.add(category[0], category[1])

        return results.__dict__


# Run this Flask application as a RESTful web service
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Add our resources to our REST API so remote clients can access them
api = Api(app)
api.add_resource(Cleaner, "/kelso/api/v1/cleaner", "/cleaner")
api.add_resource(Categories, "/kelso/api/v1/categories")
api.add_resource(Category, "/kelso/api/v1/categories/<string:name>")

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=5000, ssl_context='adhoc')