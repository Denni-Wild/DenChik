"""Initial tables"""

from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('telegram_id', sa.BigInteger, unique=True, nullable=False)
    )
    op.create_table(
        'topics',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('title', sa.Text),
        sa.Column('current_step', sa.Integer, server_default='1')
    )
    op.create_table(
        'answers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('topic_id', sa.Integer, sa.ForeignKey('topics.id')),
        sa.Column('question_index', sa.Integer),
        sa.Column('answer_text', sa.Text)
    )
    op.create_table(
        'mantras',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('topic_id', sa.Integer, sa.ForeignKey('topics.id')),
        sa.Column('text', sa.Text),
        sa.Column('step_index', sa.Integer)
    )
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('mantra_id', sa.Integer, sa.ForeignKey('mantras.id')),
        sa.Column('remind_at', sa.TIMESTAMP),
        sa.Column('sent', sa.Boolean, server_default=sa.text('false'))
    )


def downgrade() -> None:
    op.drop_table('reminders')
    op.drop_table('mantras')
    op.drop_table('answers')
    op.drop_table('topics')
    op.drop_table('users')
