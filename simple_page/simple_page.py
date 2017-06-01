from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from flask import request
import os, sys

SWIFT_URL_PROPERTIE="SWIFT_URL"
SWIFT_TEMP_URL_KEY_PROPERTIE="SWIFT_TEMP_URL_KEY"
TEMP_URL_EXPIRATION_TIME=10800

simple_page = Blueprint('simple_page', __name__, template_folder='templates')
static = Blueprint('simple_page', __name__, static_folder='static')

properties = {}
local_path = os.getcwd();
print local_path
with open('%s/simple_page/conf.properties' % (local_path), 'r') as f:
    for line in f:
        line = line.rstrip() #removes trailing whitespace and '\n' chars

        if "=" not in line: continue #skips blanks and comments w/o =
        if line.startswith("#"): continue #skips comments which contain =

        k, v = line.split("=", 1)
        properties[k] = v

@simple_page.route('/', defaults={'page': 'input'})
@simple_page.route('/<page>')
def show(page):
    try:
        return render_template('pages/%s.html' % page)
    except TemplateNotFound:
        abort(404)

@simple_page.route('/input', methods=['POST'])
def get_input_url():
    swift_url = properties.get(SWIFT_URL_PROPERTIE)
    swift_key = properties.get(SWIFT_TEMP_URL_KEY_PROPERTIE)	
    image_name = request.form['image']

    image_temp_url = os.system("swift tempurl GET %s /swift/v1/sebal_container/fetcher/inputs/%s/%s.tar.gz %s" 
   		% (TEMP_URL_EXPIRATION_TIME, image_name, image_name, swift_key))

    url = "%s%s" % (swift_url, image_temp_url)
    return render_template('pages/result.html', url=image_temp_url)

@simple_page.route('/output', methods=['POST'])
def get_output_url():
    swift_url = properties.get(SWIFT_URL_PROPERTIE)
    swift_key = properties.get(SWIFT_TEMP_URL_KEY_PROPERTIE)	
    image_name = request.form['image']
    variable = request.form['variable']

    image_temp_url = os.system("swift tempurl GET %s /swift/v1/sebal_container/fetcher/inputs/%s/%s_%s.nc %s" 
   		% (TEMP_URL_EXPIRATION_TIME, image_name, image_name, variable, swift_key))

    url = "%s%s" % (swift_url, image_temp_url)
    return render_template('pages/result.html', url=image_temp_url)    