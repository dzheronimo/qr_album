"""Normalize limits data

Revision ID: 0002
Revises: 0001
Create Date: 2025-09-06 20:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Normalize existing data to comply with new constraints."""
    
    # Normalize plans table - convert negative values to -1 (unlimited)
    op.execute("""
        UPDATE plans 
        SET max_albums = -1 
        WHERE max_albums < -1
    """)
    
    op.execute("""
        UPDATE plans 
        SET max_pages_per_album = -1 
        WHERE max_pages_per_album < -1
    """)
    
    op.execute("""
        UPDATE plans 
        SET max_media_files = -1 
        WHERE max_media_files < -1
    """)
    
    op.execute("""
        UPDATE plans 
        SET max_qr_codes = -1 
        WHERE max_qr_codes < -1
    """)
    
    op.execute("""
        UPDATE plans 
        SET max_storage_gb = -1 
        WHERE max_storage_gb < -1
    """)
    
    # Normalize usage table - convert negative values to 0
    op.execute("""
        UPDATE usage 
        SET albums_count = 0 
        WHERE albums_count < 0
    """)
    
    op.execute("""
        UPDATE usage 
        SET pages_count = 0 
        WHERE pages_count < 0
    """)
    
    op.execute("""
        UPDATE usage 
        SET media_files_count = 0 
        WHERE media_files_count < 0
    """)
    
    op.execute("""
        UPDATE usage 
        SET qr_codes_count = 0 
        WHERE qr_codes_count < 0
    """)
    
    op.execute("""
        UPDATE usage 
        SET storage_used_mb = 0 
        WHERE storage_used_mb < 0
    """)
    
    # Set NULL values to 0 in usage table
    op.execute("""
        UPDATE usage 
        SET albums_count = 0 
        WHERE albums_count IS NULL
    """)
    
    op.execute("""
        UPDATE usage 
        SET pages_count = 0 
        WHERE pages_count IS NULL
    """)
    
    op.execute("""
        UPDATE usage 
        SET media_files_count = 0 
        WHERE media_files_count IS NULL
    """)
    
    op.execute("""
        UPDATE usage 
        SET qr_codes_count = 0 
        WHERE qr_codes_count IS NULL
    """)
    
    op.execute("""
        UPDATE usage 
        SET storage_used_mb = 0 
        WHERE storage_used_mb IS NULL
    """)
    
    # Make usage columns NOT NULL after setting default values
    op.alter_column('usage', 'albums_count', nullable=False)
    op.alter_column('usage', 'pages_count', nullable=False)
    op.alter_column('usage', 'media_files_count', nullable=False)
    op.alter_column('usage', 'qr_codes_count', nullable=False)
    op.alter_column('usage', 'storage_used_mb', nullable=False)


def downgrade() -> None:
    """Revert data normalization."""
    
    # Make usage columns nullable again
    op.alter_column('usage', 'storage_used_mb', nullable=True)
    op.alter_column('usage', 'qr_codes_count', nullable=True)
    op.alter_column('usage', 'media_files_count', nullable=True)
    op.alter_column('usage', 'pages_count', nullable=True)
    op.alter_column('usage', 'albums_count', nullable=True)
    
    # Note: We don't revert the data changes as we can't know the original values
    # This is a one-way migration for data normalization
