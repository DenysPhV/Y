import unittest
from unittest.mock import MagicMock

from PhotoShare.app.repositories.comments import get_comments, create_comment, \
    update_comment, delete_comment
from PhotoShare.app.models.comment import Comment
from PhotoShare.app.models.user import User
from PhotoShare.app.schemas.comment import CommentModel

from sqlalchemy.orm import Session


class TestComment(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.test_user = User(id=1,
                              email='someemail@gmail.com',
                              role=1,
                              avatar='https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0?s=32&d'
                                     '=identicon&r=PG',
                              username='Somename',
                              confirmed=True,
                              password='secret')

    def test_get_comments(self):
        expected_comments = [Comment(id=1, content="content1"), Comment(id=2, content="content2")]
        self.session.query().filter().limit().all.return_value = expected_comments
        result = get_comments(2, 1, self.session)
        self.assertEqual(result, expected_comments)

    def test_create_comment(self):
        comment_model = CommentModel(content="Test content")
        expected_comment = Comment(id=1, content=comment_model.content, user_id=1, photo_id=1)
        self.session.add = MagicMock()
        self.session.commit = MagicMock()
        self.session.refresh = MagicMock()
        result = create_comment(comment_model, self.test_user, 1, self.session)
        # Перевірка результату
        self.assertEqual(result.content, expected_comment.content)
        self.assertEqual(result.user_id, expected_comment.user_id)
        self.assertEqual(result.photo_id, expected_comment.photo_id)

    def test_update_comment(self):
        comment_model = CommentModel(id=1, content="Updated content")
        existing_comment = Comment(id=1, content="Old content")
        self.session.query().filter().first.return_value = existing_comment
        updated_comment_obj = update_comment(comment_model, 1, self.session)
        self.assertIsNotNone(updated_comment_obj, "update_comment повернув None")
        self.assertEqual(updated_comment_obj.content, "Updated content")

    def test_delete_comment(self):
        existing_comment = Comment(id=1, content="Old content")
        self.session.query().filter().first.return_value = existing_comment
        deleted_comment = delete_comment(1, self.session)
        self.assertEqual(deleted_comment, existing_comment)
        self.session.delete.assert_called_once_with(existing_comment)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
