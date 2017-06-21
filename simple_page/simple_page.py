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
        line = line.rstrip()  # removes trailing whitespace and '\n' chars

        if "=" not in line: continue  # skips blanks and comments w/o =
        if line.startswith("#"): continue  # skips comments which contain =

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
    image_name = request.form['image']

    input_set = get_inputs(image_name)
    url_set = generate_links_for_inputs(input_set)
    return render_template('pages/result.html', url_set=url_set)


def get_inputs(image_name):
    swift_url = properties.get(ApplicationConstants.SWIFT_URL_PROPERTY)
    swift_url_storage_endpoint = properties.get(ApplicationConstants.SWIFT_URL_STORAGE_ENDPOINT_PROPERTY)
    input_files_prefix = properties.get(ApplicationConstants.SWIFT_INPUT_FILES_PREFIX_KEY_PROPERTY)
    swift_conatiner_name = properties.get(ApplicationConstants.SWIFT_CONTAINER_NAME_KEY_PROPERTY)

    # Token generation
    token_generator = OpenstackV3TokenGenerator()
    swift_auth_token = token_generator.create_token()

    input_set = set()
    cmd = "swift --os-auth-token %s --os-storage-url %s list -p %s %s" % (swift_auth_token,
                                                                          swift_url + swift_url_storage_endpoint,
                                                                          input_files_prefix + "/" + image_name,
                                                                          swift_conatiner_name)
    for output_line in subprocess.check_output(cmd, shell=True).split('\n'):
        line_split = output_line.split('/')
        if len(line_split) > 1:
            input_set.add(line_split[-2])

    return input_set


def generate_links_for_inputs(input_set):
    swift_url = properties.get(ApplicationConstants.SWIFT_URL_PROPERTY)
    swift_key = properties.get(ApplicationConstants.SWIFT_TEMP_URL_KEY_PROPERTY)

    download_links = set()
    for input_name in input_set:
        cmd = "swift tempurl GET %s /swift/v1/sebal_container/%s/%s/%s.tar.gz %s" % \
              (ApplicationConstants.TEMP_URL_EXPIRATION_TIME,
               properties.get(ApplicationConstants.SWIFT_INPUT_FILES_PREFIX_KEY_PROPERTY), input_name, input_name,
               swift_key)
        image_temp_url = subprocess.check_output(cmd, shell=True)

        url = "%s%s" % (swift_url, image_temp_url)
        download_links.add(url)

    return download_links


@simple_page.route('/output', methods=['POST'])
def get_output_url():
    image_name = request.form['image']
    variable = request.form['variable']

    output_list = get_outputs(image_name)
    url_set = generate_links_for_outputs(output_list, variable)
    return render_template('pages/result.html', url_set=url_set)


def get_outputs(image_name):
    swift_url = properties.get(ApplicationConstants.SWIFT_URL_PROPERTY)
    swift_url_storage_endpoint = properties.get(ApplicationConstants.SWIFT_URL_STORAGE_ENDPOINT_PROPERTY)
    output_files_prefix = properties.get(ApplicationConstants.SWIFT_OUTPUT_FILES_PREFIX_KEY_PROPERTY)
    swift_conatiner_name = properties.get(ApplicationConstants.SWIFT_CONTAINER_NAME_KEY_PROPERTY)

    # Token generation
    token_generator = OpenstackV3TokenGenerator()
    swift_auth_token = token_generator.create_token()

    output_set = set()
    cmd = "swift --os-auth-token %s --os-storage-url %s list -p %s %s" % (swift_auth_token,
                                                                          swift_url + swift_url_storage_endpoint,
                                                                          output_files_prefix + "/" + image_name,
                                                                          swift_conatiner_name)
    for output_line in subprocess.check_output(cmd, shell=True).split('\n'):
        line_split = output_line.split('/')
        if len(line_split) > 1:
            output_set.add(line_split[-2])

    return output_set


def generate_links_for_outputs(output_set, variable):
    swift_url = properties.get(ApplicationConstants.SWIFT_URL_PROPERTY)
    swift_key = properties.get(ApplicationConstants.SWIFT_TEMP_URL_KEY_PROPERTY)

    download_links = set()
    for output_name in output_set:
        cmd = "swift tempurl GET %s /swift/v1/sebal_container/%s/%s/%s_%s.nc %s" % \
              (ApplicationConstants.TEMP_URL_EXPIRATION_TIME,
               properties.get(ApplicationConstants.SWIFT_OUTPUT_FILES_PREFIX_KEY_PROPERTY), output_name, output_name,
               variable, swift_key)
        image_temp_url = subprocess.check_output(cmd, shell=True)

        url = "%s%s" % (swift_url, image_temp_url)
        download_links.add(url)

    return download_links
