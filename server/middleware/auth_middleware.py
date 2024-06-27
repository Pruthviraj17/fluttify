

from fastapi import HTTPException, Header
import jwt

def auth_middlware(x_auth_token = Header()):
    # check if token valid
    try:
        if not x_auth_token:
            raise HTTPException(404, 'Missing Token, Access Denied!')
        # decode token
        verified_token= jwt.decode(x_auth_token,'password_key',["HS256"])

        if not verified_token:
            raise HTTPException(404, 'Token authorization failed!')
        # get data
        uid= verified_token.get('id')
        return {'uid': uid, 'token': x_auth_token}
    except jwt.PyJWTError:
        raise HTTPException(401, 'Token is not valid, please check!')