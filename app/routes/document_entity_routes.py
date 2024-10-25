from flask import request
from app.services.document_entity_service import (
    get_all_documents,
    get_document_by_id
)

def document_entity_init_routes(app):
    @app.route('/get_doc', methods=['GET'])
    def get_document_route():
            return get_all_documents()

    @app.route('/get_doc/<document_id>', methods=['GET'])
    def get_document_routes(document_id):
            return get_document_by_id(document_id)