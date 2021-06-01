import time
import uuid
from datetime import datetime, timedelta

from django.conf import settings

import jwt
from groups.models import Group
from invites.models import Invite, InviteGroupMembership
from invites.serializers import InviteSerializer
from mails.emails import InvitationEmail
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied


def generate_invitation_token(email, workspace_slug, workspace_role_id, lang, refresh=False, invite=None):
    """
        Generates a JWT token for inviting a user to a workspace:
            - add to the token the expiration time defined in the settings
        Send by email to the email address indicated in the body
    """
    if not refresh:
        exp = time.mktime((datetime.today() + timedelta(days=settings.INVITE_KEY_EXPIRATION_DAYS)).timetuple())
        data = {"mail": email, "workspace": workspace_slug, "workspace_role_id": workspace_role_id, "exp": exp}
        token = jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")
    else:
        exp = invite.invite_estimate_timestamp_invalid
        token = invite.invite_token
    # build email
    if workspace_slug == 'munity':
        domain = "https://" + settings.APP_SUFFIX_URL
    else :
        domain = "https://" + workspace_slug + "." + settings.APP_SUFFIX_URL
    email_params = {
        "user": email,
        "domain": domain,
        "token": token,
    }
    email_factory = InvitationEmail(email_params)
    email = email_factory.create_email_msg([email], lang=lang, from_email=settings.SUPPORT_MAIL)
    email.send()
    return [token, exp]


def validate_invitation_token(token, workspace):
    """
        Check the invitation token for the new user:
            - workspace matches with the token
            - the token has not expired
            - the token has not been modified
    """
    try:
        invite = InviteSerializer(Invite.objects.get(invite_token=token)).data
    except (Invite.DoesNotExist):
        raise NotFound("invite_not_found")
    except (InviteGroupMembership.DoesNotExist):
        raise NotFound("invite_group_membership_not_found")
    try:
        body = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], option={"require_exp": True})
        if body["workspace"] != workspace:
            return {"message": "invalid_workspace"}, status.HTTP_404_NOT_FOUND
        body.pop("exp")

    except jwt.exceptions.ExpiredSignatureError:
        raise PermissionDenied("expired_token")
    except jwt.exceptions.InvalidTokenError:
        raise PermissionDenied("token_error")
    else:
        groups = invite["invite_group_memberships"]
        out_groups = []

        if len(groups) == 0:
            # raise PermissionDenied("no_assigned_groups")
            print("no assigned groups")
        else:
            for g in groups:
                # check groups exist, removes dead ones
                if Group.objects.filter(pk=uuid.UUID(g["group"]["id"])).exists():
                    out_groups.append(
                        {"id": g["group"]["id"], "group_role_id": g["group_role"]["group_role_id"]}
                    )
                    """
                    #Possible cleaner solution
                    out_groups.append(
                        InviteGroupMembershipSerializer(InviteGroupMembership.objects.get(
                            group=uuid.UUID(g['group']["id"]), invite=uuid.UUID(invite['id']))).data)
                    """
        body["groups"] = out_groups

        return body, status.HTTP_200_OK