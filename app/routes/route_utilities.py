from flask import abort, make_response
from sqlalchemy import desc
from ..db import db

def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        response = {"message": f"{cls.__name__.lower()} {model_id} invalid"}
        abort(make_response(response , 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)
    
    if not model:
        response = {"message": f"{cls.__name__.lower()} {model_id} not found"}
        abort(make_response(response, 404))
    
    return model

def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
        
    except KeyError as error:
        
        response = {"details": "Invalid data"}
        
        abort(make_response(response, 400))
    
    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201

# def get_models_with_filters(cls, filters=None):
#     query = db.select(cls)
    
#     if filters:
#         for attribute, value in filters.items():
#             if hasattr(cls, attribute):
#                 query = query.where(getattr(cls, attribute).ilike(f"%{value}%"))

#     models = db.session.scalars(query.order_by(cls.id))
#     models_response = [model.to_dict() for model in models]
#     return models_response

# def get_models_with_filters(cls, filters=None):
#     query = db.select(cls)

#     if filters:
#         sort_by = filters.get('sort_by', 'id') 
#         direction = filters.get('sort', 'asc')  

#         # Apply filtering
#         for attribute, value in filters.items():
#             if attribute in ('sort_by', 'sort'):
#                 continue
#             if hasattr(cls, attribute):
#                 query = query.where(getattr(cls, attribute).ilike(f"%{value}%"))

#         # Apply sorting
#         if hasattr(cls, sort_by):
#             sort_column = getattr(cls, sort_by)
#             if direction == 'desc':
#                 query = query.order_by(desc(sort_column))
#             else:
#                 query = query.order_by(sort_column)
#     else:
#         query = query.order_by(cls.id)

#     models = db.session.scalars(query)
#     models_response = [model.to_dict() for model in models]
#     return models_response

def get_models_with_filters(cls, filters=None, has_tasks=False):
    query = db.select(cls)

    if filters:
        # Use 'title' as default for Task, 'id' for other models
        default_sort = 'title' if cls.__name__ == "Task" else 'id'
        sort_by = filters.get('sort_by', default_sort)
        direction = filters.get('sort', 'asc')

        # Apply filtering
        for attr, value in filters.items():
            if attr in ('sort_by', 'sort'):
                continue
            if hasattr(cls, attr):
                query = query.where(getattr(cls, attr).ilike(f"%{value}%"))

        # Apply sorting
        sort_column = getattr(cls, sort_by, getattr(cls, 'id'))
        query = query.order_by(desc(sort_column) if direction == 'desc' else sort_column)
    else:
        # Default sorting
        query = query.order_by(getattr(cls, 'id'))

    models = db.session.scalars(query)
    if cls.__name__ == "Goal":
        return [model.to_dict(has_tasks=has_tasks) for model in models]
    else:
        return [model.to_dict() for model in models]
  

 