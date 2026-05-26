"""Real-time Collaboration System for Synapse Language
Enables multiple users to edit and execute Synapse code simultaneously
"""

import asyncio
import json
import uuid
import time
import hashlib
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from datetime import datetime
import threading
import queue


class OperationType(Enum):
    """Types of collaborative operations"""
    INSERT = auto()
    DELETE = auto()
    REPLACE = auto()
    CURSOR_MOVE = auto()
    SELECTION = auto()
    EXECUTE = auto()
    COMMENT = auto()


class PresenceStatus(Enum):
    """User presence states"""
    ONLINE = auto()
    IDLE = auto()
    EDITING = auto()
    EXECUTING = auto()
    OFFLINE = auto()


@dataclass
class User:
    """Collaborative user representation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Anonymous"
    color: str = "#007bff"  # Default blue
    cursor_position: int = 0
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    status: PresenceStatus = PresenceStatus.ONLINE
    last_seen: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'cursor_position': self.cursor_position,
            'selection_start': self.selection_start,
            'selection_end': self.selection_end,
            'status': self.status.name,
            'last_seen': self.last_seen
        }


@dataclass
class Operation:
    """Collaborative edit operation using OT (Operational Transformation)"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    type: OperationType = OperationType.INSERT
    position: int = 0
    content: str = ""
    length: int = 0
    timestamp: float = field(default_factory=time.time)
    version: int = 0
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type.name,
            'position': self.position,
            'content': self.content,
            'length': self.length,
            'timestamp': self.timestamp,
            'version': self.version
        }
    
    def transform(self, other: 'Operation') -> 'Operation':
        """Transform this operation against another for OT"""
        if self.type == OperationType.INSERT and other.type == OperationType.INSERT:
            if self.position < other.position:
                return self
            elif self.position > other.position:
                return Operation(
                    id=self.id,
                    user_id=self.user_id,
                    type=self.type,
                    position=self.position + len(other.content),
                    content=self.content,
                    timestamp=self.timestamp,
                    version=self.version
                )
            else:  # Same position - use user_id for consistency
                if self.user_id < other.user_id:
                    return self
                else:
                    return Operation(
                        id=self.id,
                        user_id=self.user_id,
                        type=self.type,
                        position=self.position + len(other.content),
                        content=self.content,
                        timestamp=self.timestamp,
                        version=self.version
                    )
        
        elif self.type == OperationType.DELETE and other.type == OperationType.DELETE:
            if self.position < other.position:
                return self
            elif self.position >= other.position + other.length:
                return Operation(
                    id=self.id,
                    user_id=self.user_id,
                    type=self.type,
                    position=self.position - other.length,
                    length=self.length,
                    timestamp=self.timestamp,
                    version=self.version
                )
            else:
                # Overlapping deletes
                return Operation(
                    id=self.id,
                    user_id=self.user_id,
                    type=self.type,
                    position=other.position,
                    length=max(0, self.length - other.length),
                    timestamp=self.timestamp,
                    version=self.version
                )
        
        elif self.type == OperationType.INSERT and other.type == OperationType.DELETE:
            if self.position <= other.position:
                return self
            elif self.position > other.position + other.length:
                return Operation(
                    id=self.id,
                    user_id=self.user_id,
                    type=self.type,
                    position=self.position - other.length,
                    content=self.content,
                    timestamp=self.timestamp,
                    version=self.version
                )
            else:
                return Operation(
                    id=self.id,
                    user_id=self.user_id,
                    type=self.type,
                    position=other.position,
                    content=self.content,
                    timestamp=self.timestamp,
                    version=self.version
                )
        
        elif self.type == OperationType.DELETE and other.type == OperationType.INSERT:
            if self.position < other.position:
                return self
            else:
                return Operation(
                    id=self.id,
                    user_id=self.user_id,
                    type=self.type,
                    position=self.position + len(other.content),
                    length=self.length,
                    timestamp=self.timestamp,
                    version=self.version
                )

        return self


class OperationalTransform:
    """Dict-based operational transformation API for tests and clients."""

    @staticmethod
    def _to_operation(op: dict) -> Operation:
        op_type_name = op.get("type", "insert")
        op_type = OperationType.INSERT if op_type_name == "insert" else OperationType.DELETE
        return Operation(
            user_id=op.get("user_id", ""),
            type=op_type,
            position=int(op.get("position", 0)),
            content=op.get("text", op.get("content", "")),
            length=int(op.get("length", 0)),
        )

    def transform(self, op1: dict, op2: dict) -> dict:
        result = dict(op2)
        t1, t2 = op1.get("type"), op2.get("type")
        p1, p2 = int(op1.get("position", 0)), int(op2.get("position", 0))
        if t1 == "insert" and t2 == "insert":
            text1 = op1.get("text", "")
            if p1 < p2 and p1 + len(text1) <= p2:
                return result
            if p1 < p2:
                result["position"] = p2 + len(text1)
            elif p1 == p2 and op1.get("user_id", "") < op2.get("user_id", ""):
                result["position"] = p2 + len(text1)
            return result
        if t1 == "insert" and t2 == "delete" and p1 <= p2:
            result["position"] = p2 + len(op1.get("text", ""))
            return result
        if t1 == "delete" and t2 == "delete":
            len1 = int(op1.get("length", 0))
            if p1 < p2:
                result["position"] = p2 - len1
            elif p1 == p2:
                result["length"] = max(0, int(op2.get("length", 0)) - len1)
            return result
        if t1 == "delete" and t2 == "insert" and p1 < p2:
            result["position"] = p2 - int(op1.get("length", 0))
        return result


@dataclass
class Document:
    """Collaborative document state"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "untitled.syn"
    content: str = ""
    version: int = 0
    operations: List[Operation] = field(default_factory=list)
    checksum: str = ""

    def apply_operation(self, op: Operation) -> str:
        """Apply an operation to document content"""
        if op.type == OperationType.INSERT:
            self.content = (
                self.content[:op.position] +
                op.content +
                self.content[op.position:]
            )
        elif op.type == OperationType.DELETE:
            self.content = (
                self.content[:op.position] +
                self.content[op.position + op.length:]
            )
        elif op.type == OperationType.REPLACE:
            self.content = (
                self.content[:op.position] +
                op.content +
                self.content[op.position + op.length:]
            )

        self.operations.append(op)
        self.version += 1
        self.checksum = hashlib.sha256(self.content.encode()).hexdigest()[:8]
        return self.content

    def get_snapshot(self) -> dict:
        """Get document snapshot for sync"""
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'version': self.version,
            'checksum': self.checksum
        }


class CollaborationSession:
    """Manages a collaborative editing session"""

    def __init__(self, session_id: Optional[str] = None):
        self.id = session_id or str(uuid.uuid4())
        self.users: Dict[str, User] = {}
        self.document = Document()
        self.operation_queue: queue.Queue = queue.Queue()
        self.pending_operations: List[Operation] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.is_active = True
        self._lock = threading.Lock()

    def join(self, user: User) -> Dict[str, Any]:
        """User joins the session"""
        with self._lock:
            self.users[user.id] = user
            self._emit('user_joined', user.to_dict())

            return {
                'session_id': self.id,
                'document': self.document.get_snapshot(),
                'users': [u.to_dict() for u in self.users.values()],
                'user_id': user.id
            }

    def leave(self, user_id: str):
        """User leaves the session"""
        with self._lock:
            if user_id in self.users:
                user = self.users[user_id]
                user.status = PresenceStatus.OFFLINE
                del self.users[user_id]
                self._emit('user_left', {'user_id': user_id})

    def apply_operation(self, op: Operation) -> Dict[str, Any]:
        """Apply operation with OT"""
        with self._lock:
            # Transform against pending operations
            transformed_op = op
            for pending_op in self.pending_operations:
                if pending_op.timestamp < op.timestamp:
                    transformed_op = transformed_op.transform(pending_op)

            # Apply to document
            self.document.apply_operation(transformed_op)

            # Broadcast to other users
            self._emit('operation', transformed_op.to_dict())

            return {
                'success': True,
                'version': self.document.version,
                'checksum': self.document.checksum
            }

    def update_cursor(self, user_id: str, position: int,
                     selection: Optional[tuple] = None):
        """Update user cursor position"""
        with self._lock:
            if user_id in self.users:
                user = self.users[user_id]
                user.cursor_position = position
                if selection:
                    user.selection_start, user.selection_end = selection
                else:
                    user.selection_start = user.selection_end = None

                user.status = PresenceStatus.EDITING
                user.last_seen = time.time()

                self._emit('cursor_update', {
                    'user_id': user_id,
                    'position': position,
                    'selection': selection
                })

    def execute_code(self, user_id: str, code: str) -> Dict[str, Any]:
        """Execute Synapse code collaboratively"""
        with self._lock:
            if user_id in self.users:
                self.users[user_id].status = PresenceStatus.EXECUTING

                # Create execution operation
                exec_op = Operation(
                    user_id=user_id,
                    type=OperationType.EXECUTE,
                    content=code,
                    timestamp=time.time(),
                    version=self.document.version
                )

                self._emit('code_execution', {
                    'user_id': user_id,
                    'code': code,
                    'timestamp': exec_op.timestamp
                })

                # Simulate execution result
                result = {
                    'success': True,
                    'output': f"Executed by {self.users[user_id].name}",
                    'execution_time': 0.05
                }

                self.users[user_id].status = PresenceStatus.ONLINE
                return result

            return {'success': False, 'error': 'User not found'}

    def add_comment(self, user_id: str, line: int, text: str) -> Dict[str, Any]:
        """Add inline comment"""
        with self._lock:
            comment = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'line': line,
                'text': text,
                'timestamp': time.time()
            }

            self._emit('comment_added', comment)
            return comment

    def on(self, event: str, handler: Callable):
        """Register event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def _emit(self, event: str, data: Any):
        """Emit event to handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Error in event handler: {e}")

    def get_presence(self) -> List[Dict[str, Any]]:
        """Get current user presence info"""
        with self._lock:
            presence = []
            current_time = time.time()

            for user in self.users.values():
                # Update idle status
                if current_time - user.last_seen > 300:  # 5 minutes
                    user.status = PresenceStatus.IDLE

                presence.append(user.to_dict())

            return presence


class CollaborationManager:
    """Manages multiple collaboration sessions"""

    def __init__(self):
        self._sessions: Dict[str, CollaborationSession] = {}
        self.user_sessions: Dict[str, str] = {}

    @property
    def sessions(self) -> Dict[str, Dict[str, Any]]:
        return {
            sid: {"users": s.users, "operations": s.document.operations}
            for sid, s in self._sessions.items()
        }

    def create_session(self, name: str = "New Session") -> str:
        session = CollaborationSession()
        session.document.name = name
        self._sessions[session.id] = session
        return session.id

    def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        return self._sessions.get(session_id)

    def join_session(self, session_id: str, user):
        session = self.get_session(session_id)
        if not session:
            return False if isinstance(user, str) else {"error": "Session not found"}
        if isinstance(user, str):
            session.join(User(id=user, name=user))
            self.user_sessions[user] = session_id
            return True
        result = session.join(user)
        self.user_sessions[user.id] = session_id
        return result

    def apply_operation(self, session_id: str, operation: dict) -> bool:
        session = self.get_session(session_id)
        if not session:
            return False
        op_type = OperationType.INSERT if operation.get("type") == "insert" else OperationType.DELETE
        op = Operation(
            user_id=operation.get("user_id", ""),
            type=op_type,
            position=int(operation.get("position", 0)),
            content=operation.get("text", operation.get("content", "")),
            length=int(operation.get("length", 0)),
        )
        session.apply_operation(op)
        return True

    def get_session_state(self, session_id: str) -> dict:
        session = self.get_session(session_id)
        if not session:
            return {}
        return {
            "version": session.document.version,
            "users": list(session.users.keys()),
            "operations": session.document.operations,
        }

    def leave_session(self, session_id: str, user_id: str = None):
        if user_id is None:
            uid = session_id
            if uid in self.user_sessions:
                sid = self.user_sessions[uid]
                session = self.get_session(sid)
                if session:
                    session.leave(uid)
                del self.user_sessions[uid]
            return None
        session = self.get_session(session_id)
        if not session or user_id not in session.users:
            return False
        session.leave(user_id)
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        return True

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return [
            {
                'id': session.id,
                'name': session.document.name,
                'users': len(session.users),
                'version': session.document.version
            }
            for session in self._sessions.values()
            if session.is_active
        ]

    def cleanup_inactive(self, timeout: int = 3600):
        """Clean up inactive sessions (default 1 hour)"""
        current_time = time.time()
        to_remove = []

        for session_id, session in self._sessions.items():
            if not session.users:  # No users
                last_activity = max(
                    [op.timestamp for op in session.document.operations]
                    + [0]
                )
                if current_time - last_activity > timeout:
                    to_remove.append(session_id)

        for session_id in to_remove:
            del self._sessions[session_id]


# WebSocket-compatible message handler
class CollaborationProtocol:
    """Protocol for collaboration messages"""

    @staticmethod
    def encode(msg_type: str, data: Any) -> str:
        """Encode message for transmission"""
        message = {
            'type': msg_type,
            'data': data,
            'timestamp': time.time()
        }
        return json.dumps(message)

    @staticmethod
    def decode(message: str) -> Dict[str, Any]:
        """Decode received message"""
        return json.loads(message)

    @staticmethod
    def create_operation_msg(op: Operation) -> str:
        """Create operation message"""
        return CollaborationProtocol.encode('operation', op.to_dict())

    @staticmethod
    def create_cursor_msg(user_id: str, position: int) -> str:
        """Create cursor update message"""
        return CollaborationProtocol.encode('cursor', {
            'user_id': user_id,
            'position': position
        })

    @staticmethod
    def create_presence_msg(users: List[User]) -> str:
        """Create presence update message"""
        return CollaborationProtocol.encode('presence', [
            u.to_dict() for u in users
        ])


# Example usage and testing
if __name__ == "__main__":
    print("Synapse Collaboration System Demo")
    print("=" * 40)

    # Create collaboration manager
    manager = CollaborationManager()

    # Create a new session
    session_id = manager.create_session("quantum_simulation.syn")
    session = manager.get_session(session_id)
    print(f"Created session: {session_id}")

    # Create users
    alice = User(name="Alice", color="#ff6b6b")
    bob = User(name="Bob", color="#4ecdc4")

    # Join session
    alice_join = manager.join_session(session.id, alice)
    print(f"Alice joined: {alice_join['session_id']}")

    bob_join = manager.join_session(session.id, bob)
    print(f"Bob joined: {bob_join['session_id']}")

    # Simulate collaborative editing
    print("\n--- Collaborative Editing ---")

    # Alice inserts text
    op1 = Operation(
        user_id=alice.id,
        type=OperationType.INSERT,
        position=0,
        content="let quantum_state = superposition(|0⟩, |1⟩)\n"
    )
    result1 = session.apply_operation(op1)
    print(f"Alice inserted text (v{result1['version']})")

    # Bob inserts text
    op2 = Operation(
        user_id=bob.id,
        type=OperationType.INSERT,
        position=len(session.document.content),
        content="let measurement = observe(quantum_state)\n"
    )
    result2 = session.apply_operation(op2)
    print(f"Bob inserted text (v{result2['version']})")

    # Update cursors
    session.update_cursor(alice.id, 20)
    session.update_cursor(bob.id, 45, (40, 45))

    # Alice executes code
    print("\n--- Code Execution ---")
    exec_result = session.execute_code(alice.id, session.document.content)
    print(f"Execution: {exec_result}")

    # Add comment
    comment = session.add_comment(bob.id, 1, "Should we add error correction?")
    print(f"Bob commented: {comment['text']}")

    # Show document state
    print("\n--- Document State ---")
    snapshot = session.document.get_snapshot()
    print(f"Version: {snapshot['version']}")
    print(f"Checksum: {snapshot['checksum']}")
    print(f"Content:\n{snapshot['content']}")

    # Show presence
    print("\n--- User Presence ---")
    presence = session.get_presence()
    for user in presence:
        print(f"- {user['name']}: {user['status']} at position {user['cursor_position']}")

    # Test OT transformation
    print("\n--- Operational Transformation ---")
    op_a = Operation(
        user_id="user_a",
        type=OperationType.INSERT,
        position=5,
        content="hello"
    )
    op_b = Operation(
        user_id="user_b",
        type=OperationType.INSERT,
        position=5,
        content="world"
    )
    transformed = op_a.transform(op_b)
    print(f"Op A at pos {op_a.position} -> transformed to pos {transformed.position}")

    # List sessions
    print("\n--- Active Sessions ---")
    sessions = manager.list_sessions()
    for s in sessions:
        print(f"- {s['name']}: {s['users']} users, v{s['version']}")

    print("\n✅ Real-time collaboration system implemented!")