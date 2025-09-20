"""
Test suite for Real-time Collaboration features
"""

import unittest
from synapse_lang.collaboration import CollaborationManager, OperationalTransform


class TestOperationalTransform(unittest.TestCase):
    def setUp(self):
        self.ot = OperationalTransform()

    def test_insert_operations(self):
        """Test insert operation transformations"""
        # Two users inserting at different positions
        op1 = {"type": "insert", "position": 5, "text": "hello", "user_id": "user1"}
        op2 = {"type": "insert", "position": 10, "text": "world", "user_id": "user2"}

        transformed = self.ot.transform(op1, op2)

        # op2's position should not change since op1 is before it
        self.assertEqual(transformed["position"], 10)

    def test_concurrent_inserts_same_position(self):
        """Test concurrent inserts at same position"""
        op1 = {"type": "insert", "position": 5, "text": "hello", "user_id": "user1"}
        op2 = {"type": "insert", "position": 5, "text": "world", "user_id": "user2"}

        transformed = self.ot.transform(op1, op2)

        # op2 should be shifted by length of op1's text
        self.assertEqual(transformed["position"], 10)

    def test_delete_operations(self):
        """Test delete operation transformations"""
        op1 = {"type": "delete", "position": 5, "length": 3, "user_id": "user1"}
        op2 = {"type": "delete", "position": 10, "length": 2, "user_id": "user2"}

        transformed = self.ot.transform(op1, op2)

        # op2's position should shift back by op1's deleted length
        self.assertEqual(transformed["position"], 7)

    def test_mixed_operations(self):
        """Test mixed insert and delete operations"""
        op1 = {"type": "insert", "position": 5, "text": "hello", "user_id": "user1"}
        op2 = {"type": "delete", "position": 10, "length": 2, "user_id": "user2"}

        transformed = self.ot.transform(op1, op2)

        # op2's position should shift forward by op1's insert length
        self.assertEqual(transformed["position"], 15)


class TestCollaborationManager(unittest.TestCase):
    def setUp(self):
        self.manager = CollaborationManager()
        self.session_id = self.manager.create_session("test_project")

    def test_create_session(self):
        """Test session creation"""
        self.assertIsNotNone(self.session_id)
        self.assertIn(self.session_id, self.manager.sessions)

    def test_join_session(self):
        """Test users joining session"""
        user1 = self.manager.join_session(self.session_id, "user1")
        user2 = self.manager.join_session(self.session_id, "user2")

        self.assertTrue(user1)
        self.assertTrue(user2)

        session = self.manager.sessions[self.session_id]
        self.assertIn("user1", session["users"])
        self.assertIn("user2", session["users"])

    def test_apply_operation(self):
        """Test applying operations to session"""
        self.manager.join_session(self.session_id, "user1")

        operation = {
            "type": "insert",
            "position": 0,
            "text": "Hello World",
            "user_id": "user1"
        }

        result = self.manager.apply_operation(self.session_id, operation)

        self.assertTrue(result)
        session = self.manager.sessions[self.session_id]
        self.assertEqual(len(session["operations"]), 1)

    def test_concurrent_operations(self):
        """Test handling concurrent operations"""
        self.manager.join_session(self.session_id, "user1")
        self.manager.join_session(self.session_id, "user2")

        # Simulate concurrent edits
        op1 = {
            "type": "insert",
            "position": 0,
            "text": "Hello ",
            "user_id": "user1",
            "version": 0
        }

        op2 = {
            "type": "insert",
            "position": 0,
            "text": "World ",
            "user_id": "user2",
            "version": 0
        }

        self.manager.apply_operation(self.session_id, op1)
        self.manager.apply_operation(self.session_id, op2)

        session = self.manager.sessions[self.session_id]
        self.assertEqual(len(session["operations"]), 2)

    def test_get_session_state(self):
        """Test getting session state"""
        self.manager.join_session(self.session_id, "user1")

        operation = {
            "type": "insert",
            "position": 0,
            "text": "Test content",
            "user_id": "user1"
        }
        self.manager.apply_operation(self.session_id, operation)

        state = self.manager.get_session_state(self.session_id)

        self.assertEqual(state["version"], 1)
        self.assertIn("user1", state["users"])
        self.assertEqual(len(state["operations"]), 1)

    def test_leave_session(self):
        """Test users leaving session"""
        self.manager.join_session(self.session_id, "user1")
        self.manager.join_session(self.session_id, "user2")

        result = self.manager.leave_session(self.session_id, "user1")

        self.assertTrue(result)
        session = self.manager.sessions[self.session_id]
        self.assertNotIn("user1", session["users"])
        self.assertIn("user2", session["users"])

    def test_invalid_session(self):
        """Test handling invalid session ID"""
        result = self.manager.join_session("invalid_id", "user1")
        self.assertFalse(result)

        operation = {"type": "insert", "position": 0, "text": "Test"}
        result = self.manager.apply_operation("invalid_id", operation)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()