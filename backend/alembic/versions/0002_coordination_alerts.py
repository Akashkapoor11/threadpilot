"""coordination alerts

Revision ID: 0002_coordination_alerts
"""
from alembic import op
import sqlalchemy as sa

revision='0002_coordination_alerts'; down_revision='0001_initial'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('alerts',
        sa.Column('id',sa.String(40),primary_key=True),
        sa.Column('signal_id',sa.String(40),nullable=False),
        sa.Column('recipient',sa.String(160),nullable=False),
        sa.Column('channel',sa.String(40),nullable=False),
        sa.Column('status',sa.String(30),nullable=False,server_default='QUEUED'),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=True),
    )
    op.create_index('ix_alerts_signal_id','alerts',['signal_id'])

def downgrade():
    op.drop_index('ix_alerts_signal_id',table_name='alerts')
    op.drop_table('alerts')
