import unittest
from unittest.mock import MagicMock

from PhotoShare.app.repositories.comments import get_comments, create_comment, \
    update_comment, delete_comment
from PhotoShare.app.models.comment import Comment
from PhotoShare.app.models.user import User
from PhotoShare.app.schemas.comment import CommentModel

from sqlalchemy.orm import Session

"""
Є проблеми з постом треба звернути увагу та доробити цей тест
"""


class CommentTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.test_user = User(id=1,
                              login='SomeLogin',
                              email='someemail@gmail.com',
                              role=1,
                              user_pic_url='https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0?s=32&d'
                                           '=identicon&r=PG',
                              name='Somename',
                              is_active=True,
                              password_checksum='secret')

    async def test_get_comments(self):
        comments = [Comment(id=1, content="content1"), Comment(id=2, content="content2")]
        self.session.query().filter().offset().limit().all.return_value = comments
        result = await get_comments(2, 1, self.session)
        self.assertEqual(result, comments)

    async def test_create_comment(self):
        user = User(id=1)
        comment_model = CommentModel(content="Test content")
        comment = Comment(id=1, content=comment_model.content, user_id=user.id, post_id=1)
        result = await create_comment(comment_model, user, 1, self.session)
        self.assertEqual(result, comment)

    async def test_update_comment(self):
        comment_model = CommentModel(id=1, content="Updated content")
        existing_comment = Comment(id=1, content="Old content")
        self.session.query().filter().first.return_value = existing_comment
        updated_comment = await update_comment(comment_model, 1, self.session).content
        self.assertEqual(updated_comment.content, "Updated content")

    async def test_delete_comment(self):
        existing_comment = Comment(id=1, content="Old content")
        self.session.query().filter().first.return_value = existing_comment
        deleted_comment = await delete_comment(1, self.session)
        self.assertEqual(deleted_comment, existing_comment)
        self.session.delete.assert_called_once_with(existing_comment)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
