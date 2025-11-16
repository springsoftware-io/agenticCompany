"""Auth0 authentication service for FastAPI"""
import httpx
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from functools import lru_cache
import logging

from config import config
from database import get_db
from db_models import User

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


class Auth0Error(Exception):
    """Auth0 related errors"""
    pass


class Auth0Service:
    """Service for Auth0 authentication and token verification"""
    
    @staticmethod
    @lru_cache(maxsize=1)
    async def get_jwks():
        """Get JWKS from Auth0 (cached)"""
        if not config.auth0_domain:
            raise Auth0Error("Auth0 domain not configured")
        
        jwks_url = f"https://{config.auth0_domain}/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            return response.json()
    
    @staticmethod
    async def verify_decode_jwt(token: str) -> dict:
        """Verify and decode JWT token from Auth0"""
        try:
            if not config.auth0_domain or not config.auth0_audience:
                raise Auth0Error("Auth0 not configured")
            
            # Get the public key from Auth0
            jwks = await Auth0Service.get_jwks()
            
            # Get the data in the header
            unverified_header = jwt.get_unverified_header(token)
            
            # Choose our key
            rsa_key = {}
            if 'kid' not in unverified_header:
                raise Auth0Error('Authorization malformed')

            for key in jwks['keys']:
                if key['kid'] == unverified_header['kid']:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
            
            if rsa_key:
                try:
                    # Validate the token using the rsa_key
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=['RS256'],
                        audience=config.auth0_audience,
                        issuer=f"https://{config.auth0_domain}/"
                    )
                    return payload

                except jwt.ExpiredSignatureError:
                    raise Auth0Error('Token expired')

                except jwt.JWTClaimsError:
                    raise Auth0Error('Incorrect claims. Please check the audience and issuer')
                
                except Exception as e:
                    raise Auth0Error(f'Unable to parse authentication token: {str(e)}')

            raise Auth0Error('Unable to find a suitable key')

        except Exception as e:
            if isinstance(e, Auth0Error):
                raise e
            raise Auth0Error(f'Token verification failed: {str(e)}')

    @staticmethod
    async def get_user_info(token: str) -> dict:
        """Get user information from Auth0"""
        try:
            if not config.auth0_domain:
                raise Auth0Error("Auth0 domain not configured")
            
            headers = {'Authorization': f'Bearer {token}'}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{config.auth0_domain}/userinfo",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Auth0Error(f'Failed to get user info: {response.status_code}')
                    
        except Exception as e:
            raise Auth0Error(f'Failed to get user info: {str(e)}')

    @staticmethod
    def get_or_create_user(db: Session, auth0_user_info: dict) -> User:
        """Get or create user in local database from Auth0 user info"""
        try:
            # Extract user info
            email = auth0_user_info.get('email')
            if not email:
                raise Auth0Error('Email not found in user info')
            
            # Check if user exists
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                # Create new user
                full_name = auth0_user_info.get('name') or email.split('@')[0]
                
                user = User(
                    email=email,
                    full_name=full_name,
                    hashed_password="",  # No password for Auth0 users
                    is_active=True,
                    oauth_provider='auth0',
                    oauth_id=auth0_user_info.get('sub')
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
                
                logger.info(f"Created new user from Auth0: {email}")
            
            else:
                # Update existing user info if needed
                if not user.oauth_id and auth0_user_info.get('sub'):
                    user.oauth_id = auth0_user_info.get('sub')
                    user.oauth_provider = 'auth0'
                    db.commit()
            
            return user
            
        except Exception as e:
            db.rollback()
            raise Auth0Error(f'Failed to get or create user: {str(e)}')
    
    @staticmethod
    async def get_user_from_jwt(token: str, db: Session) -> Optional[User]:
        """Get user from JWT token
        
        Uses the 'sub' claim to look up user in local database.
        Only calls Auth0 API if user doesn't exist locally.
        
        Args:
            token: JWT token
            db: Database session
            
        Returns:
            User object if valid, None otherwise
        """
        try:
            # Verify token with Auth0
            payload = await Auth0Service.verify_decode_jwt(token)
            
            # Get the Auth0 user ID (sub claim)
            auth0_id = payload.get('sub')
            if not auth0_id:
                raise Auth0Error('No sub claim in JWT')
            
            # Try to find user in local database by oauth_id
            user = db.query(User).filter(User.oauth_id == auth0_id).first()
            
            if user:
                # User exists in database, return it
                logger.info(f"Found user in database: {user.email}")
                return user
            
            # User doesn't exist locally, need to fetch from Auth0 and create
            logger.info(f"User {auth0_id} not in database, fetching from Auth0")
            user_info = await Auth0Service.get_user_info(token)
            user = Auth0Service.get_or_create_user(db, user_info)
            
            return user
            
        except Auth0Error as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying JWT token: {str(e)}")
            return None


async def get_current_user_auth0(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from Auth0 JWT token (required)"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user = await Auth0Service.get_user_from_jwt(token, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_optional_user_auth0(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise return None (optional)"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = await Auth0Service.get_user_from_jwt(token, db)
        
        if user and user.is_active:
            return user
        return None
    except Exception as e:
        logger.warning(f"Optional auth failed: {str(e)}")
        return None
