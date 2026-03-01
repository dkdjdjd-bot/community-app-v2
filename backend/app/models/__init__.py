# 모델 패키지 초기화
# 모든 모델을 여기서 import하여 SQLModel.metadata에 등록
from app.models.user import User  # noqa: F401
from app.models.post import Post  # noqa: F401
from app.models.comment import Comment  # noqa: F401
