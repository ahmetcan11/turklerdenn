from typing import Any, List, Optional
from api import deps
from fastapi import APIRouter, Body, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from starlette import status

from api.api_v1.endpoints.test_endpoints import get_public_user_profile
from models.general import General, GeneralImage, Comment
from schemas.General import general_schema
from models.general import General as general_model
from models.user import User as user_model
from crud import crud_general, crud_comment, crud_like
from utils.googleBucket import upload_general_images, upload_free_item_images

router = APIRouter()


@router.post("/addComment")
def add_comment(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int = Body(None),
    comment: str = Body(None),
    current_user: general_model = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new general post...
    """
    public_profile = get_public_user_profile(current_user.id, db)

    comment = crud_general.crud_general.add_comment(
        db, comment=general_schema.CommentCreate(
            comment=comment
        ), owner_id=current_user.id, post_id=post_id, first_name=public_profile.get("first_name"),
        last_name=public_profile.get("last_name")
    )
    return comment


@router.post("/reply")
def reply_to_comment(
    *,
    db: Session = Depends(deps.get_db),
    parent_comment_id: int = Body(None),
    reply: str = Body(None),
    current_user: general_model = Depends(deps.get_current_active_user)
) -> Any:
    """
    Reply to an existing comment...
    """
    public_profile = get_public_user_profile(current_user.id, db)
    reply_comment = crud_general.crud_general.reply_to_comment(
        db, reply=general_schema.CommentCreate(
            comment=reply,
        ), owner_id=current_user.id, parent_comment_id=parent_comment_id,first_name=public_profile.get("first_name"),
        last_name=public_profile.get("last_name")
    )
    return reply_comment


@router.get("/comments/{post_id}")
def get_comments_with_replies(post_id: int,
                              db: Session = Depends(deps.get_db)):
    comments = crud_comment.get_comments(db, post_id)
    comments_with_replies = []

    for comment in comments:
        comment.replies = crud_comment.get_comment_replies(db, comment.id)
        comments_with_replies.append(comment)

    return comments_with_replies


@router.post("/upvote/{comment_id}")
def upvote_comment(
    comment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: general_model = Depends(deps.get_current_active_user)
):
    up_down_obj = crud_like.get_liked_comment(db=db, user_id=current_user.id, comment_id=comment_id)
    if up_down_obj:
        if up_down_obj.downvote:
            # make downvote False in the updowngeneralpost table
            crud_like.remove_comment_downvote(db=db, user_id=current_user.id, comment_id=comment_id)
            # Remove donvote number from general post
            comment = crud_comment.remove_downvote_comment(db=db,
                                                                         user_id=current_user.id,
                                                                         comment_id=comment_id)
            return comment
    if not up_down_obj:
        crud_like.add_comment_upvote(db=db, user_id=current_user.id, comment_id=comment_id)
        comment = crud_comment.upvote_comment(db=db,
                                                                     user_id=current_user.id,
                                                                     comment_id=comment_id)
        return comment
    elif up_down_obj.upvote:
        crud_like.remove_comment_upvote(db=db, user_id=current_user.id, comment_id=comment_id)
        comment = crud_comment.remove_upvote_comment(db=db,
                                                             user_id=current_user.id,
                                                             comment_id=comment_id)
        return comment
    elif not up_down_obj.upvote:
        crud_like.add_comment_upvote(db=db, user_id=current_user.id, comment_id=comment_id)
        comment = crud_comment.upvote_comment(db=db,
                                                             user_id=current_user.id,
                                                             comment_id=comment_id)
        return comment
    else:
        crud_like.add_comment_upvote(db=db, user_id=current_user.id, comment_id=comment_id)
        comment = crud_comment.upvote_comment(db=db,
                                                      user_id=current_user.id,
                                                      comment_id=comment_id)
        return comment


@router.post("/downvote/{comment_id}")
def downvote_comment(
    comment_id: int,
    db: Session = Depends(deps.get_db),
    current_user: general_model = Depends(deps.get_current_active_user)
):
    up_down_obj = crud_like.get_liked_comment(db=db, user_id=current_user.id, comment_id=comment_id)
    if up_down_obj:
        if up_down_obj.upvote:
            # make downvote False in the updown table
            crud_like.remove_comment_upvote(db=db, user_id=current_user.id, comment_id=comment_id)
            # Remove donvote number from general post
            comment = crud_comment.remove_upvote_comment(db=db, user_id=current_user.id, comment_id=comment_id)
            return comment
    if not up_down_obj:
        crud_like.add_comment_downvote(db=db, user_id=current_user.id, comment_id=comment_id)
        comment = crud_comment.downvote_comment(db=db,
                                                                     user_id=current_user.id,
                                                                     comment_id=comment_id)
        return comment
    elif up_down_obj.downvote:
        crud_like.remove_comment_downvote(db=db, user_id=current_user.id, comment_id=comment_id)
        comment = crud_comment.remove_downvote_comment(db=db,
                                                                            user_id=current_user.id,
                                                                            comment_id=comment_id)
        return comment
    elif not up_down_obj.downvote:
        crud_like.add_comment_downvote(db=db, user_id=current_user.id, comment_id=comment_id)
        comment = crud_comment.downvote_comment(db=db,
                                                                     user_id=current_user.id,
                                                                     comment_id=comment_id)
        return comment
    else:
        crud_like.add_comment_downvote(db=db, user_id=current_user.id, comment_id=comment_id)
        comment = crud_comment.downvote_comment(db=db,
                                                                     user_id=current_user.id,
                                                                     comment_id=comment_id)
        return comment
