from abc import ABCMeta, abstractmethod


class TokenGenerator:
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_token(self):
        pass
