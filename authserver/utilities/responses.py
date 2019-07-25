"""Standardized Response Bodies."""

from collections import OrderedDict

# Collection of exceptions and associated error messages.
EXCEPTION_TYPES = {
    'IntegrityError': 'A record with one or more unique fields already exists. Please re-check your request and try again.',
    'Unknown': 'An unknown error has occured and has been reported to our technical team.'
}


class ResponseBody(object):
    """A response body handler."""

    def __init__(self):
        self.base_response = OrderedDict({
            'status': 'OK',
            'code': 200,
            'messages': [],
            'request': [],
            'response': []
        })

    def get_all_response(self, results: list, message: str = 'Successfully retrieved resources'):
        """Retrieve a list of responses.

        Args:
            results (list): The list of results to return.
            message (str): The message to include in the response.

        Returns:
            dict, int: The response object and HTTP status code.

        """

        response = self.base_response.copy()
        del(response['request'])
        response['messages'].append('{}.'.format(message))
        response['response'] = results
        return response, response['code']

    def get_one_response(self, result: dict, message: str = 'Successfully retrieved resource', request=None):
        """Retrieve a single response.

        Args:
            result (obj): The result to return.
            message (str): The message to include in the response.
            request: The original request to include in the response.

        Returns:
            dict, int: The response object and HTTP status code.

        """

        response = self.base_response.copy()
        if request is None:
            del(response['request'])
        else:
            response['request'] = request
        response['messages'].append('{}.'.format(message))
        response['response'] = result
        return response, response['code']

    def not_found_response(self, id: any):
        """Return an object not found message.

        Args:
            id (any): The identifier of the object that could not be located.

        Returns:
            dict, int: The response object and HTTP status code.

        """

        response = self.base_response.copy()
        response['status'] = 'Error'
        response['code'] = 404
        response['messages'].append('No resource with identifier \'{}\' found.'.format(id))
        del(response['response'])
        del(response['request'])
        return response, response['code']

    def method_not_allowed_response(self):
        """Return a method not allowed message.

        Returns:
            dict, int: The response object and HTTP status code.

        """
        response = self.base_response.copy()
        response['status'] = 'Error'
        response['code'] = 405
        response['messages'].append('Method not allowed.')
        del(response['response'])
        del(response['request'])
        return response, response['code']

    def empty_request_body_response(self):
        """Return an empty request body message.

        Returns:
            dict, int: The response object and HTTP status code.
        """
        response = self.base_response.copy()
        response['status'] = 'Error'
        response['code'] = 400
        response['messages'].append('Empty request body.')
        del(response['response'])
        del(response['request'])
        return response, response['code']

    def custom_response(self, status='Error', code=400, messages=[], request=[], response=[]):
        """Return a custom response message.

        Args:
            status (str): The status type
            code (int): The HTTP status code
            messages (list): The list of messages to include
            request (list): The HTTP request body
            response (list): The HTTP response body

        Returns:
            dict, int: The response object and HTTP status code.
        """

        custom_response = OrderedDict()
        custom_response['status'] = status
        custom_response['code'] = code
        if len(messages) > 0:
            custom_response['messages'] = messages
        if len(request) > 0:
            custom_response['request'] = request
        if len(response) > 0:
            custom_response['response'] = response

        return custom_response, custom_response['code']

    def exception_response(self, exception_name: str, code=400, request=[], resp=[]):
        """Returns a custom response from an exception.

        Args:
            status (str): The status type
            exception_name (str): The name of the exception
            code (int): The HTTP status code
            request (list): The HTTP request body
            resp (list): The HTTP response body

        Returns:
            dict, int: The response object and HTTP status code.
        """

        response = self.base_response.copy()
        response['status'] = 'Error'
        response['code'] = code
        if exception_name in EXCEPTION_TYPES:
            response['messages'].append(EXCEPTION_TYPES[exception_name])
        else:
            response['messages'].append(EXCEPTION_TYPES['Unknown'])
        if len(request) > 0:
            response['request'].append(request)
        else:
            del(response['request'])

        if len(resp) > 0:
            response['response'].append(resp)
        else:
            del(response['response'])

        return response, response['code']

    def successful_creation_response(self, resource_name: str, resource_id, request=[]):
        """Returns a successful creation message for a given resource.

        Args:
            resource_name (str): The name to assign to the resource.
            resource_id (any): The unique identifier for the new resource.
            request (list): The original HTTP request.

        Returns:
            dict, int: The response object and HTTP status code.

        """
        response = self.base_response.copy()
        response['code'] = 201
        response['messages'].append('Successfully created new {} record.'.format(resource_name))
        if len(request) > 0:
            response['request'].append(request)
        else:
            del(response['request'])
        response['response'].append({'id': resource_id})

        return response, response['code']

    def successful_update_response(self, resource_name: str, resource_id, request=[]):
        """Returns a successful creation message for a given resource.

        Args:
            resource_name (str): The name to assign to the resource.
            resource_id (any): The unique identifier for the new resource.
            request (list): The original HTTP request.

        Returns:
            dict, int: The response object and HTTP status code.

        """
        response = self.base_response.copy()
        response['code'] = 200
        response['messages'].append('Successfully updated existing {} record.'.format(resource_name))
        if len(request) > 0:
            request['id'] = resource_id
            response['request'].append(request)
        else:
            del(response['request'])
        del response['response']

        return response, response['code']

    def successful_delete_response(self, resource_name: str, resource_id, resp=[]):
        """Returns a successful creation message for a given resource.

        Args:
            resource_name (str): The name to assign to the resource.
            resource_id (any): The unique identifier for the new resource.
            request (list): The original HTTP request.
            resp (list): The HTTP response body.

        Returns:
            dict, int: The response object and HTTP status code.

        """
        response = self.base_response.copy()
        response['code'] = 200
        response['messages'].append('Successfully deleted {} record.'.format(resource_name))
        response['request'].append({'id': resource_id})
        if len(resp) > 0:
            response['response'].append(resp)
        else:
            del response['response']

        return response, response['code']
