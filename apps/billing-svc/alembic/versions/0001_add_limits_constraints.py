"""Add limits constraints and indexes

Revision ID: 0001
Revises: 
Create Date: 2025-09-06 20:21:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add CHECK constraints and indexes for limits validation."""
    
    # Add CHECK constraints for plans table
    op.create_check_constraint(
        'ck_plans_max_albums_valid',
        'plans',
        'max_albums IS NULL OR max_albums >= -1'
    )
    
    op.create_check_constraint(
        'ck_plans_max_pages_per_album_valid',
        'plans',
        'max_pages_per_album IS NULL OR max_pages_per_album >= -1'
    )
    
    op.create_check_constraint(
        'ck_plans_max_media_files_valid',
        'plans',
        'max_media_files IS NULL OR max_media_files >= -1'
    )
    
    op.create_check_constraint(
        'ck_plans_max_qr_codes_valid',
        'plans',
        'max_qr_codes IS NULL OR max_qr_codes >= -1'
    )
    
    op.create_check_constraint(
        'ck_plans_max_storage_gb_valid',
        'plans',
        'max_storage_gb IS NULL OR max_storage_gb >= -1'
    )
    
    # Add CHECK constraints for usage table
    op.create_check_constraint(
        'ck_usage_albums_count_non_negative',
        'usage',
        'albums_count >= 0'
    )
    
    op.create_check_constraint(
        'ck_usage_pages_count_non_negative',
        'usage',
        'pages_count >= 0'
    )
    
    op.create_check_constraint(
        'ck_usage_media_files_count_non_negative',
        'usage',
        'media_files_count >= 0'
    )
    
    op.create_check_constraint(
        'ck_usage_qr_codes_count_non_negative',
        'usage',
        'qr_codes_count >= 0'
    )
    
    op.create_check_constraint(
        'ck_usage_storage_used_mb_non_negative',
        'usage',
        'storage_used_mb >= 0'
    )
    
    # Add indexes for better performance
    op.create_index(
        'ix_usage_user_id_period',
        'usage',
        ['user_id', 'period_start', 'period_end']
    )
    
    op.create_index(
        'ix_subscriptions_user_id_status',
        'subscriptions',
        ['user_id', 'status']
    )
    
    op.create_index(
        'ix_subscriptions_status_end_date',
        'subscriptions',
        ['status', 'end_date']
    )


def downgrade() -> None:
    """Remove CHECK constraints and indexes."""
    
    # Drop indexes
    op.drop_index('ix_subscriptions_status_end_date', table_name='subscriptions')
    op.drop_index('ix_subscriptions_user_id_status', table_name='subscriptions')
    op.drop_index('ix_usage_user_id_period', table_name='usage')
    
    # Drop CHECK constraints for usage table
    op.drop_constraint('ck_usage_storage_used_mb_non_negative', 'usage', type_='check')
    op.drop_constraint('ck_usage_qr_codes_count_non_negative', 'usage', type_='check')
    op.drop_constraint('ck_usage_media_files_count_non_negative', 'usage', type_='check')
    op.drop_constraint('ck_usage_pages_count_non_negative', 'usage', type_='check')
    op.drop_constraint('ck_usage_albums_count_non_negative', 'usage', type_='check')
    
    # Drop CHECK constraints for plans table
    op.drop_constraint('ck_plans_max_storage_gb_valid', 'plans', type_='check')
    op.drop_constraint('ck_plans_max_qr_codes_valid', 'plans', type_='check')
    op.drop_constraint('ck_plans_max_media_files_valid', 'plans', type_='check')
    op.drop_constraint('ck_plans_max_pages_per_album_valid', 'plans', type_='check')
    op.drop_constraint('ck_plans_max_albums_valid', 'plans', type_='check')
