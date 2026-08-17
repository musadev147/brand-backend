from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.engine import Engine
from sqladmin import Admin, ModelView
from typing import Union

from app.models.user import User, PasswordReset
from app.models.profile import ClientProfile, CreatorProfile, KYCDocument
from app.models.campaign import Campaign, Proposal
from app.models.gig import Gig
from app.models.chat import ChatThread, ChatMessage
from app.models.banner import PromoBanner

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.email, User.role, User.is_email_verified, User.is_kyc_verified, User.created_at]
    column_searchable_list = [User.name, User.email]
    column_details_exclude_list = [User.password]
    form_excluded_columns = ["password", "created_at", "updated_at", "deleted_at", "client_profile", "creator_profile", "kyc_documents"]
    icon = "fa-solid fa-user"

class PasswordResetAdmin(ModelView, model=PasswordReset):
    column_list = [PasswordReset.id, PasswordReset.email, PasswordReset.otp, PasswordReset.is_verified, PasswordReset.expires_at]
    column_searchable_list = [PasswordReset.email]
    icon = "fa-solid fa-key"

class ClientProfileAdmin(ModelView, model=ClientProfile):
    column_list = [ClientProfile.id, ClientProfile.company_name, ClientProfile.business_type, ClientProfile.location, ClientProfile.country]
    column_searchable_list = [ClientProfile.company_name, ClientProfile.country]
    icon = "fa-solid fa-building"

class CreatorProfileAdmin(ModelView, model=CreatorProfile):
    column_list = [CreatorProfile.id, CreatorProfile.followers_count, CreatorProfile.avg_views, CreatorProfile.engagement_rate, CreatorProfile.location]
    icon = "fa-solid fa-wand-magic-sparkles"

class KYCDocumentAdmin(ModelView, model=KYCDocument):
    column_list = [KYCDocument.id, KYCDocument.document_type, KYCDocument.document_number, KYCDocument.status, KYCDocument.created_at]
    column_searchable_list = [KYCDocument.document_number]
    icon = "fa-solid fa-id-card"

class CampaignAdmin(ModelView, model=Campaign):
    column_list = [Campaign.id, Campaign.title, Campaign.product_name, Campaign.budget, Campaign.deadline, Campaign.status]
    column_searchable_list = [Campaign.title, Campaign.product_name]
    icon = "fa-solid fa-bullhorn"

class ProposalAdmin(ModelView, model=Proposal):
    column_list = [Proposal.id, Proposal.campaign_id, Proposal.creator_user_id, Proposal.price, Proposal.delivery_time, Proposal.status]
    icon = "fa-solid fa-paper-plane"

class GigAdmin(ModelView, model=Gig):
    column_list = [Gig.id, Gig.creator_user_id, Gig.title, Gig.price, Gig.platform, Gig.category, Gig.is_active]
    column_searchable_list = [Gig.title, Gig.category]
    icon = "fa-solid fa-palette"

class ChatThreadAdmin(ModelView, model=ChatThread):
    column_list = [ChatThread.id, ChatThread.chat_key, ChatThread.client_user_id, ChatThread.creator_user_id, ChatThread.last_message_at]
    column_searchable_list = [ChatThread.chat_key]
    icon = "fa-solid fa-comments"

class ChatMessageAdmin(ModelView, model=ChatMessage):
    column_list = [ChatMessage.id, ChatMessage.chat_thread_id, ChatMessage.sender_user_id, ChatMessage.sender_role, ChatMessage.is_contract, ChatMessage.created_at]
    column_searchable_list = [ChatMessage.text]
    icon = "fa-solid fa-comment"

class PromoBannerAdmin(ModelView, model=PromoBanner):
    column_list = [PromoBanner.id, PromoBanner.title, PromoBanner.button_text, PromoBanner.redirect_to, PromoBanner.is_active, PromoBanner.sort_order]
    column_searchable_list = [PromoBanner.title, PromoBanner.subtitle]
    icon = "fa-solid fa-images"

def setup_admin(app: FastAPI, engine: Union[Engine, AsyncEngine]) -> Admin:
    """Sets up the SQLAdmin dashboard."""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(os.path.dirname(current_dir), "templates")
    print(f"📁 Template directory configured: {templates_dir}")
    admin = Admin(app, engine, title="Brand Bridge Admin CRM", templates_dir=templates_dir)
    
    # Register views
    admin.add_view(UserAdmin)
    admin.add_view(PasswordResetAdmin)
    admin.add_view(ClientProfileAdmin)
    admin.add_view(CreatorProfileAdmin)
    admin.add_view(KYCDocumentAdmin)
    admin.add_view(CampaignAdmin)
    admin.add_view(ProposalAdmin)
    admin.add_view(GigAdmin)
    admin.add_view(ChatThreadAdmin)
    admin.add_view(ChatMessageAdmin)
    admin.add_view(PromoBannerAdmin)
    
    return admin
