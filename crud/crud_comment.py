from typing import List, Type, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exc
from crud.base import CRUDBase
from models.general import General, GeneralImage, Comment
from schemas.General.general_schema import GeneralCreate, GeneralBase, CommentCreate


def get_comments(db: Session, post_id: int):
    comments = db.query(Comment).filter(Comment.post_id == post_id,
                             Comment.parent_comment_id.is_(None)).all()
    return comments


def get_comment_replies(db: Session, comment_id: int) -> List[Comment]:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return []

    replies = db.query(Comment).filter(Comment.parent_comment_id == comment_id).all()
    for reply in replies:
        reply.replies = get_comment_replies(db, reply.id)
    return replies


def upvote_comment(db: Session, *, comment_id: int, user_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        comment.upvote += 1
        db.commit()
        db.refresh(comment)
        return comment


def downvote_comment(db: Session, *, comment_id: int, user_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        comment.downvote += 1
        db.commit()
        db.refresh(comment)
        return comment


def remove_upvote_comment(db: Session, *, comment_id: int, user_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        comment.upvote -= 1
        db.commit()
        db.refresh(comment)
        return comment

def downvote_general_post(self, db: Session, *, general_post_id: int, user_id: int):
    general_post = db.query(General).filter(General.id == general_post_id).first()
    if general_post:
        general_post.downvote += 1
        db.commit()
        db.refresh(general_post)
        return general_post


def remove_downvote_comment(db: Session, *, comment_id: int, user_id: int):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        comment.downvote -= 1
        db.commit()
        db.refresh(comment)
        return comment
