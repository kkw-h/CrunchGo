from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate

class UserService:
    @staticmethod
    async def authenticate_wechat(db: AsyncSession, code: str) -> User:
        """
        Mock WeChat authentication.
        In a real scenario, this would:
        1. Call WeChat API (jscode2session) with the code to get openid and session_key.
        2. Verify the response.
        """
        
        # Mock implementation: 
        # For testing, we'll generate a deterministic openid based on the code
        # or just use a fixed one if code is 'test_code'
        if code == "test_code":
            mock_openid = "mock_openid_123456"
        else:
            # Simulate getting openid from WeChat
            mock_openid = f"wx_openid_{code}"
            
        # Check if user exists
        result = await db.execute(select(User).where(User.openid == mock_openid))
        user = result.scalars().first()
        
        if not user:
            # Create new user
            new_user = User(
                openid=mock_openid,
                nickname=f"User_{code[:5]}",
                point_balance=0
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user
            
        return user

user_service = UserService()
