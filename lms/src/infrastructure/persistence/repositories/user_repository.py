"""
Django User Repository Implementation
"""
from typing import List, Optional
from django.contrib.auth.models import User
from django.db import transaction

from ....domain.interfaces.repositories import IUserRepository
from ....domain.entities.user import UserEntity, UserProfile, GlobalRole
from ..models.user import UserProfileModel


class DjangoUserRepository(IUserRepository):
    """
    Django ORM implementation of IUserRepository
    """
    
    def _to_entity(self, user: User) -> UserEntity:
        """Convert Django User model to UserEntity"""
        profile = None
        try:
            if hasattr(user, 'profile') and user.profile:
                # Get full URL for avatar
                avatar_url = None
                if user.profile.avatar:
                    avatar_url = user.profile.avatar.url
                
                profile = UserProfile(
                    id=user.profile.id,
                    user_id=user.id,
                    full_name=user.profile.full_name,
                    role=GlobalRole(user.profile.role),
                    avatar=avatar_url,
                    phone=user.profile.phone,
                    bio=user.profile.bio,
                    created_at=user.profile.created_at,
                    updated_at=user.profile.updated_at,
                )
        except UserProfileModel.DoesNotExist:
            pass
        
        return UserEntity(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash=user.password,
            is_active=user.is_active,
            last_login=user.last_login,
            profile=profile,
            created_at=user.date_joined,
        )
    
    def _to_model(self, entity: UserEntity) -> User:
        """Convert UserEntity to Django User model"""
        if entity.id:
            user = User.objects.get(pk=entity.id)
            user.username = entity.username
            user.email = entity.email
            user.is_active = entity.is_active
        else:
            user = User(
                username=entity.username,
                email=entity.email,
                is_active=entity.is_active,
            )
        return user
    
    @transaction.atomic
    def save(self, entity: UserEntity) -> None:
        """Save user entity to database"""
        user = self._to_model(entity)
        
        if not entity.id:
            # New user - set password
            user.set_password(entity.password_hash)  # Assumes raw password for new users
        else:
            # Existing user - check if password changed (raw password, not hash)
            if entity.password_hash and not entity.password_hash.startswith('pbkdf2_'):
                user.set_password(entity.password_hash)
        
        user.save()
        entity.id = user.id
        
        # Save profile
        if entity.profile:
            profile, created = UserProfileModel.objects.get_or_create(user=user)
            profile.full_name = entity.profile.full_name
            profile.role = entity.profile.role.value
            # Handle avatar file upload
            if entity.profile.avatar:
                if hasattr(entity.profile.avatar, 'read'):
                    # It's a file object
                    profile.avatar = entity.profile.avatar
                elif isinstance(entity.profile.avatar, str) and entity.profile.avatar:
                    # It's already a path string, keep it
                    pass
            profile.phone = entity.profile.phone
            profile.bio = entity.profile.bio
            profile.save()
            entity.profile.id = profile.id
    
    def delete(self, entity_id: int) -> bool:
        """Delete user by ID"""
        try:
            user = User.objects.get(pk=entity_id)
            user.delete()
            return True
        except User.DoesNotExist:
            return False
    
    def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Find user by ID"""
        try:
            user = User.objects.select_related('profile').get(pk=user_id)
            return self._to_entity(user)
        except User.DoesNotExist:
            return None
    
    def find_by_email(self, email: str) -> Optional[UserEntity]:
        """Find user by email"""
        try:
            user = User.objects.select_related('profile').get(email=email)
            return self._to_entity(user)
        except User.DoesNotExist:
            return None
    
    def find_by_username(self, username: str) -> Optional[UserEntity]:
        """Find user by username"""
        try:
            user = User.objects.select_related('profile').get(username=username)
            return self._to_entity(user)
        except User.DoesNotExist:
            return None
    
    def exists_by_email(self, email: str) -> bool:
        """Check if user with email exists"""
        return User.objects.filter(email=email).exists()
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[UserEntity]:
        """Get all users with pagination"""
        users = User.objects.select_related('profile').all()[offset:offset + limit]
        return [self._to_entity(u) for u in users]
    
    def find_by_role(self, role: str) -> List[UserEntity]:
        """Find users by role"""
        users = User.objects.select_related('profile').filter(
            profile__role=role
        )
        return [self._to_entity(u) for u in users]

