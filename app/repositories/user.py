from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    def __init__(self):
        self.model = User

    def get(self, db: Session, id: int):
        return db.get(User, id)

    def get_all(self, db: Session):
        return db.query(User).all()

    def get_by_username(self, db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    def count(self, db: Session) -> int:
        return db.query(User).count()

    def create(self, db: Session, data: dict):
        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, db_obj: User, data: dict):
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: User):
        db.delete(db_obj)
        db.commit()


user_repository = UserRepository()