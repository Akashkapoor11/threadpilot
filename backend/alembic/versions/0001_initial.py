"""initial schema

Revision ID: 0001_initial
"""
from alembic import op
import sqlalchemy as sa

revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('project_meta',sa.Column('id',sa.String(40),primary_key=True),sa.Column('name',sa.String(160),nullable=False),sa.Column('code',sa.String(40),nullable=False),sa.Column('demo_mode',sa.Boolean(),nullable=False,server_default=sa.true()))
    op.create_table('stakeholders',sa.Column('id',sa.String(40),primary_key=True),sa.Column('name',sa.String(120),nullable=False),sa.Column('role',sa.String(120),nullable=False),sa.Column('focus',sa.String(240),nullable=False),sa.Column('initials',sa.String(8),nullable=False),sa.Column('status',sa.String(30),nullable=False,server_default='ACTIVE'))
    op.create_table('messages',sa.Column('id',sa.String(40),primary_key=True),sa.Column('channel',sa.String(50),nullable=False),sa.Column('sender',sa.String(120),nullable=False),sa.Column('time_label',sa.String(30),nullable=False),sa.Column('text',sa.Text(),nullable=False),sa.Column('tag',sa.String(40),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))
    op.create_table('signals',sa.Column('id',sa.String(40),primary_key=True),sa.Column('type',sa.String(30),nullable=False),sa.Column('severity',sa.String(20),nullable=False),sa.Column('title',sa.String(240),nullable=False),sa.Column('detail',sa.Text(),nullable=False),sa.Column('source_ids',sa.String(500),nullable=False),sa.Column('owner',sa.String(200),nullable=False),sa.Column('confidence',sa.Integer(),nullable=False),sa.Column('status',sa.String(30),nullable=False),sa.Column('impact',sa.Text(),nullable=False),sa.Column('why',sa.Text(),nullable=False),sa.Column('action',sa.Text(),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))
    op.create_table('actions',sa.Column('id',sa.String(40),primary_key=True),sa.Column('priority',sa.String(10),nullable=False),sa.Column('title',sa.String(240),nullable=False),sa.Column('owner',sa.String(160),nullable=False),sa.Column('due',sa.String(60),nullable=False),sa.Column('status',sa.String(30),nullable=False),sa.Column('reason',sa.Text(),nullable=False),sa.Column('source_ids',sa.String(500),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),nullable=True))
    op.create_table('audit',sa.Column('id',sa.String(40),primary_key=True),sa.Column('event',sa.String(80),nullable=False),sa.Column('entity',sa.String(50),nullable=False),sa.Column('entity_id',sa.String(80),nullable=False),sa.Column('detail',sa.Text(),nullable=False),sa.Column('ts',sa.DateTime(timezone=True),nullable=True))

def downgrade():
    for t in ['audit','actions','signals','messages','stakeholders','project_meta']: op.drop_table(t)
