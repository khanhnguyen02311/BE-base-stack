from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from components.functions.security import handle_get_current_user_oauth2
from components.functions.chat import handle_create_new_group, handle_get_participant_by_account_and_group, \
    handle_get_participants_by_account, handle_get_participants_by_group
from components.storages import postgres_schemas as p_schemas, postgres_models as p_models

router = APIRouter(prefix="/group")


@router.get("/list")
def get_group_list(account: Annotated[p_models.Account, Depends(handle_get_current_user_oauth2)]):
    result_list = []
    list_personal_participant = handle_get_participants_by_account(account.id)
    for i in list_personal_participant:
        result_list.append(i.id_chatgroup)
    return result_list


@router.get("/list/{groupid}/messages")
def get_message_list(account: Annotated[p_models.Account, Depends(handle_get_current_user_oauth2)], groupid: str):
    valid_participant = handle_get_participant_by_account_and_group(account.id, groupid)
    if valid_participant is not None:
        return True  # get messages for later
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail="You are not a participant of the group")


@router.get("/list/{groupid}/participants")
def get_group_participant_list(account: Annotated[p_models.Account, Depends(handle_get_current_user_oauth2)],
                               groupid: str):
    valid_participant = handle_get_participant_by_account_and_group(account.id, groupid)
    if valid_participant is not None:
        result_list = []
        participants = handle_get_participants_by_group(groupid)
        for i in participants:
            result_list.append(i.id_account)
        return result_list
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                         detail="You are not a participant of the group")


@router.post("/create")
def create_new_group(data: p_schemas.AccountSchema,
                     account: Annotated[p_models.Account, Depends(handle_get_current_user_oauth2)]):
    try:
        created_group = handle_create_new_group([data.id, account.id])
        return created_group
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
