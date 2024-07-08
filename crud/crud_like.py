from sqlalchemy.orm import Session, joinedload
from models.general import General, GeneralImage, Comment
from models.UpDownGeneralPost import UpDownGeneralPost
from models.UpDownComment import UpDownComment


def get_liked_general(db: Session, user_id: int, general_post_id: int):
    liked_post = db.query(UpDownGeneralPost).filter(UpDownGeneralPost.general_post_id == general_post_id,
                             UpDownGeneralPost.user_id == user_id).first()
    return liked_post


def get_liked_comment(db: Session, user_id: int, comment_id: int):
    liked_comment = db.query(UpDownComment).filter(UpDownComment.comment_id == comment_id,
                             UpDownComment.user_id == user_id).first()
    return liked_comment


def add_general_upvote(db: Session, user_id: int, general_post_id: int):
    upvote_obj = db.query(UpDownGeneralPost).filter(UpDownGeneralPost.general_post_id == general_post_id,
                                                    UpDownGeneralPost.user_id == user_id).first()
    if not upvote_obj:
        new_like = UpDownGeneralPost(user_id=user_id, general_post_id=general_post_id, upvote=True)
        db.add(new_like)
        db.commit()
        return new_like
    else:
        upvote_obj.upvote = True
        db.add(upvote_obj)
        db.commit()
        return upvote_obj  # Return the newly created like entry


def remove_general_upvote(db: Session, user_id: int, general_post_id: int):
    downvote_obj = db.query(UpDownGeneralPost).filter(UpDownGeneralPost.general_post_id == general_post_id,
                                                    UpDownGeneralPost.user_id == user_id).first()

    if not downvote_obj:
        new_downvote = UpDownGeneralPost(user_id=user_id, general_post_id=general_post_id, upvote=False)
        db.add(new_downvote)
        db.commit()
        return new_downvote
    else:
        downvote_obj.upvote = False
        db.add(downvote_obj)
        db.commit()
    return downvote_obj


def add_general_downvote(db: Session, user_id: int, general_post_id: int):
    upDownObj = db.query(UpDownGeneralPost).filter(UpDownGeneralPost.general_post_id == general_post_id,
                                                    UpDownGeneralPost.user_id == user_id).first()
    if not upDownObj:
        upDownObj = UpDownGeneralPost(user_id=user_id, general_post_id=general_post_id, downvote=True)
        db.add(upDownObj)
        db.commit()
        return upDownObj
    else:
        upDownObj.downvote = True
        db.add(upDownObj)
        db.commit()
        return upDownObj  # Return the newly created like entry


def add_comment_downvote(db: Session, user_id: int, comment_id: int):
    upDownObj = db.query(UpDownComment).filter(UpDownComment.comment_id == comment_id,
                                                    UpDownComment.user_id == user_id).first()
    if not upDownObj:
        upDownObj = UpDownComment(user_id=user_id, comment_id=comment_id, downvote=True)
        db.add(upDownObj)
        db.commit()
        return upDownObj
    else:
        upDownObj.downvote = True
        db.add(upDownObj)
        db.commit()
        return upDownObj  # Return the newly created like entry


def remove_general_downvote(db: Session, user_id: int, general_post_id: int):
    upDownObj = db.query(UpDownGeneralPost).filter(UpDownGeneralPost.general_post_id == general_post_id,
                                                      UpDownGeneralPost.user_id == user_id).first()

    if not upDownObj:
        upDownObj = UpDownGeneralPost(user_id=user_id, general_post_id=general_post_id, downvote=False)
        db.add(upDownObj)
        db.commit()
        return upDownObj
    else:
        upDownObj.downvote = False
        db.add(upDownObj)
        db.commit()
    return upDownObj


def remove_comment_downvote(db: Session, user_id: int, comment_id: int):
    upDownObj = db.query(UpDownComment).filter(UpDownComment.comment_id == comment_id,
                                                      UpDownComment.user_id == user_id).first()

    if not upDownObj:
        upDownObj = UpDownComment(user_id=user_id, comment_id=comment_id, downvote=False)
        db.add(upDownObj)
        db.commit()
        return upDownObj
    else:
        upDownObj.downvote = False
        db.add(upDownObj)
        db.commit()
    return upDownObj


def add_comment_upvote(db: Session, user_id: int, comment_id: int):
    upvote_obj = db.query(UpDownComment).filter(UpDownComment.comment_id == comment_id,
                                                    UpDownComment.user_id == user_id).first()
    if not upvote_obj:
        comment = UpDownComment(user_id=user_id, comment_id=comment_id, upvote=True)
        db.add(comment)
        db.commit()
        return comment
    else:
        upvote_obj.upvote = True
        db.add(upvote_obj)
        db.commit()
        return upvote_obj  # Return the newly created like entry


def remove_comment_upvote(db: Session, user_id: int, comment_id: int):
    downvote_obj = db.query(UpDownComment).filter(UpDownComment.comment_id == comment_id,
                                                    UpDownComment.user_id == user_id).first()

    if not downvote_obj:
        new_downvote = UpDownGeneralPost(user_id=user_id, comment_id=comment_id, upvote=False)
        db.add(new_downvote)
        db.commit()
        return new_downvote
    else:
        downvote_obj.upvote = False
        db.add(downvote_obj)
        db.commit()
    return downvote_obj
