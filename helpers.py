from flask import jsonify, request
from functools import wraps

server_transaction_id = 0

def get_next_transaction_id():
    global server_transaction_id
    server_transaction_id += 1
    return server_transaction_id

def alpaca_response(
    value=None,
    error_number=0,
    error_message='',
    client_id=0,
    server_id=None
):
    response = {
        "ClientTransactionID": int(client_id),
        "ServerTransactionID": int(server_id),
        "ErrorNumber": int(error_number),
        "ErrorMessage": error_message
    }

    if value is not None:
        response["Value"] = value

    return jsonify(response)


def alpaca_endpoint(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        server_id = get_next_transaction_id()
        client_id = request.args.get('ClientTransactionID', 0)
        return fn(client_id=int(client_id), server_id=server_id, *args, **kwargs)
    return wrapper
