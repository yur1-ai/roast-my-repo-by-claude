from sqlalchemy import Column, Index, Integer, String, Text

from app.database import Base


class Roast(Base):
    __tablename__ = "roasts"

    id = Column(String, primary_key=True)
    repo_url = Column(Text, nullable=False)
    repo_owner = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    brutality_level = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    repo_metadata = Column(Text, nullable=True)
    analysis_result = Column(Text, nullable=True)
    roast_result = Column(Text, nullable=True)
    overall_score = Column(Integer, nullable=True)
    letter_grade = Column(String, nullable=True)
    created_at = Column(String, nullable=False)
    completed_at = Column(String, nullable=True)

    __table_args__ = (
        Index("idx_roasts_status", "status"),
        Index("idx_roasts_created", "created_at"),
        Index("idx_roasts_repo", "repo_owner", "repo_name"),
    )
