from core.plugins.identity import token_generator
from utils.constants import ApplicationConstants
import ConfigParser
import requests
import logging


class OpenstackV3TokenGenerator(token_generator.TokenGenerator):

    def __init__(self):
        super(token_generator.TokenGenerator, self).__init__()
        self.__config = ConfigParser.ConfigParser()
        self.__config.read(ApplicationConstants.DEFAULT_CONFIG_FILE_PATH)
        self.__keystone_url = self.config_section_map("SectionOne")["keystone_auth_url"]
        self.__keystone_v3_auth_endpoint = self.config_section_map("SectionOne")["keystone_v3_auth_endpoint"]
        self.__project_id = self.config_section_map("SectionTwo")["keystone_project_id"]
        self.__user_id = self.config_section_map("SectionTwo")["keystone_user_id"]
        self.__password = self.config_section_map("SectionTwo")["keystone_password"]

    def config_section_map(self, section):
        dict1 = {}
        options = self.__config.options(section)
        for option in options:
            try:
                dict1[option] = self.__config.get(section, option)
                if dict1[option] == -1:
                    logging.debug("skip: %s", option)
            except Exception as e:
                logging.debug(str(e))
                dict1[option] = None
        return dict1

    def create_token(self):
        if not self.validate_credentials(self.__project_id, self.__user_id, self.__password):
            return None
        json_payload = self.mount_json(self.__project_id, self.__user_id, self.__password)
        current_token_endpoint = self.__keystone_url + self.__keystone_v3_auth_endpoint
        response = self.do_post_request(current_token_endpoint, json_payload)
        return self.get_token_from_response(response)

    @staticmethod
    def validate_credentials(project_id, user_id, password):
        if (project_id is None) or (not project_id):
            return False
        if (user_id is None) or (not user_id):
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
