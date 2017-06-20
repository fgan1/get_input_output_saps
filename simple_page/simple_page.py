from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from flask import request
from core.plugins.identity.openstack.openstack_token_plugin import OpenstackV3TokenGenerator
from utils.constants import ApplicationConstants
import subprocess
import os


simple_page = Blueprint('simple_page', __name__, template_folder='templates')
static = Blueprint('simple_page', __name__, static_folder='static')

properties = {}
local_path = os.getcwd()
print local_path
with open('%s/simple_page/conf.properties' % local_path, 'r') as f:
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
    swift_url = properties.get(ApplicationConstants.SWIFT_URL_PROPERTY)
    swift_key = properties.get(ApplicationConstants.SWIFT_TEMP_URL_KEY_PROPERTY)
    image_name = request.form['image']
    print swift_url

    cmd = "swift tempurl GET %s /swift/v1/sebal_container/fetcher/inputs/%s/%s.tar.gz %s" % \
          (ApplicationConstants.TEMP_URL_EXPIRATION_TIME, image_name, image_name, swift_key)
    image_temp_url = subprocess.check_output(cmd, shell=True)

    url = "%s%s" % (swift_url, image_temp_url)
    return render_template('pages/result.html', url=url)


@simple_page.route('/output', methods=['POST'])
def get_output_url():
    swift_url = properties.get(ApplicationConstants.SWIFT_URL_PROPERTY)
    swift_key = properties.get(ApplicationConstants.SWIFT_TEMP_URL_KEY_PROPERTY)
    image_name = request.form['image']
    variable = request.form['variable']

    cmd = "swift tempurl GET %s /swift/v1/sebal_container/fetcher/images/%s/%s_%s.nc %s" % \
          (ApplicationConstants.TEMP_URL_EXPIRATION_TIME, image_name, image_name, variable, swift_key)
    image_temp_url = subprocess.check_output(cmd, shell=True)

    url = "%s%s" % (swift_url, image_temp_url)
    return render_template('pages/result.html', url=url)    


@simple_page.route('/input-list', methods=['GET'])
def get_input_list_url():
    swift_url = properties.get(ApplicationConstants.SWIFT_URL_PROPERTY)
    swift_url_storage_endpoint = properties.get(ApplicationConstants.SWIFT_URL_STORAGE_ENDPOINT_PROPERTY)
    input_files_prefix = properties.get(ApplicationConstants.SWIFT_INPUT_FILES_PREFIX_KEY_PROPERTY)
    swift_conatiner_name = properties.get(ApplicationConstants.SWIFT_CONTAINER_NAME_KEY_PROPERTY)

    # Token generation
    token_generator = OpenstackV3TokenGenerator()
    swift_auth_token = token_generator.create_token()
    print swift_auth_token

    input_set = set()
    cmd = "swift --os-auth-token %s --os-storage-url %s list -p %s %s" % (swift_auth_token,
                                                                          swift_url + swift_url_storage_endpoint,
                                                                          input_files_prefix, swift_conatiner_name)
    for output_line in subprocess.check_output(cmd, shell=True).split('\n'):
        line_split = output_line.split('/')
        input_set.add(line_split[-2])
    
    return render_template('pages/input-list.html', input_set=input_set)


@simple_page.route('/output-list', methods=['GET'])
def get_output_list_url():
    swift_url = properties.get(ApplicationConstants.SWIFT_URL_PROPERTY)
    swift_url_storage_endpoint = properties.get(ApplicationConstants.SWIFT_URL_STORAGE_ENDPOINT_PROPERTY)
    output_files_prefix = properties.get(ApplicationConstants.SWIFT_INPUT_FILES_PREFIX_KEY_PROPERTY)
    swift_conatiner_name = properties.get(ApplicationConstants.SWIFT_CONTAINER_NAME_KEY_PROPERTY)

    # Token generation
    token_generator = OpenstackV3TokenGenerator()
    swift_auth_token = token_generator.create_token()
    print swift_auth_token

    output_set = set()
    cmd = "swift --os-auth-token %s --os-storage-url %s list -p %s %s" % (swift_auth_token,
                                                                          swift_url + swift_url_storage_endpoint,
                                                                          output_files_prefix, swift_conatiner_name)
    for output_line in subprocess.check_output(cmd, shell=True).split('\n'):
        line_split = output_line.split('/')
        output_set.add(line_split[-2])
    
    return render_template('pages/output-list.html', output_set=output_set)
