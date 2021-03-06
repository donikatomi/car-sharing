"""empty message

Revision ID: 10f44a63040f
Revises: 
Create Date: 2020-02-11 14:44:27.720795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10f44a63040f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=45), nullable=True),
    sa.Column('last_name', sa.String(length=45), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('listings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('location_from', sa.String(), nullable=True),
    sa.Column('location_to', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('price', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('listing_id', sa.Integer(), nullable=False),
    sa.Column('receiver_id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('requests',
    sa.Column('accepted', sa.Boolean(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('listing_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['listing_id'], ['listings.id'], onupdate='cascade', ondelete='cascade'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='cascade', ondelete='cascade'),
    sa.PrimaryKeyConstraint('user_id', 'listing_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('requests')
    op.drop_table('notifications')
    op.drop_table('listings')
    op.drop_table('users')
    op.drop_table('locations')
    # ### end Alembic commands ###
