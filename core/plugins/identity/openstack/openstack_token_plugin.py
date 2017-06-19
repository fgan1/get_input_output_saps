from core.plugins.identity import token_generator
from utils.constants import ApplicationConstants
import ConfigParser
import requests
import logging
import os


class OpenstackV3TokenGenerator(token_generator.TokenGenerator):

    def __init__(self):
        super(token_generator.TokenGenerator, self).__init__()
        self.__properties = self.get_properties()
        self.__keystone_url = self.__properties.get(ApplicationConstants.KEYSTONE_AUTH_URL_KEY_PROPERTY)
        self.__keystone_url_endpoint = self.__properties.get(ApplicationConstants.KEYSTONE_AUTH_ENDPOINT_KEY_PROPERTY)
        self.__project_id = self.__properties.get(ApplicationConstants.KEYSTONE_PROJECT_ID_KEY_PROPERTY)
        self.__user_id = self.__properties.get(ApplicationConstants.KEYSTONE_USER_ID_KEY_PROPERTY)
        self.__password = self.__properties.get(ApplicationConstants.KEYSTONE_PASSWORD_KEY_PROPERTY)

    def create_token(self):
        logging.debug("Creating openstackV3 token...")
        if not self.validate_credentials(self.__project_id, self.__user_id, self.__password):
            logging.error("Credentials are invalid")
            return None
        json_payload = self.mount_json(self.__project_id, self.__user_id, self.__password)
        current_token_endpoint = self.__keystone_url + self.__keystone_url_endpoint
        response = self.do_post_request(current_token_endpoint, json_payload)
        return self.get_token_from_response(response)

    @staticmethod
    def get_properties():
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

        return properties

    @staticmethod
    def validate_credentials(project_id, user_id, password):
        if (project_id is None) or (not project_id):
            logging.error("Invalid value %s for project_id" % project_id)
            return False
        if (user_id is None) or (not user_id):
            logging.error("Invalid value %s for user_id" % user_id)
            return False
        if (password is None) or (not password):
            return False
        return True

    @staticmethod
    def mount_json(project_id, user_id, password):
        data = '{"auth":{"identity":{"methods":["password"],"password":{"user":{"id":"' + user_id + '",' \
               '"password":"' + password + '"}}},"scope":{"project":{"id":"' + project_id + '"}}}}'
        return data

    @staticmethod
    def do_post_request(current_token_endpoint, json_payload):
        header = {ApplicationConstants.CONTENT_TYPE: ApplicationConstants.JSON_CONTENT_TYPE}
        return requests.post(current_token_endpoint, data=json_payload, headers=header)

    @staticmethod
    def get_token_from_response(response):
        headers = response.headers

        access_id = None
        for key in headers.keys():
            if key == 'X_SUBJECT_TOKEN':
                access_id = headers.get(key)
        return access_id
