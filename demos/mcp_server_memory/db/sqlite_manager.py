"""
SQLite database manager for the MCP Memory Server.
"""

import os
import sys
from typing import List, Dict, Any, Optional

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import using local path
from config import SQLITE_PATH, MEMORY_COLLECTION, TOPICS_COLLECTION, SUMMARY_COLLECTION
from utils.helpers import timestamp
from .sqlite_connection import SQLiteConnection


class SQLiteManager:
    """Manager for SQLite database operations."""

    def __init__(self):
        """Initialize the SQLite manager."""
        self._ensure_dir_exists()

    def _ensure_dir_exists(self):
        """Ensure the database directory exists."""
        try:
            os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
        except Exception as e:
            print(f"Error creating directory: {e}")

    def _query_fetch(self, query: str, all: bool = True) -> list | None:
        try:
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                if all:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()
                return result

        except Exception as e:
            print(f"Error while querying: {e}")
            return None

    def initialize(self, reset: bool = False) -> bool:
        """Initialize the SQLite database.
        
        Args:
            reset: Whether to reset the database
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f'SQLiteManager: Initializing SQLite database at {SQLITE_PATH}')
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()

                if reset:
                    cursor.execute(f"DROP TABLE IF EXISTS {MEMORY_COLLECTION}")
                    cursor.execute(f"DROP TABLE IF EXISTS {TOPICS_COLLECTION}")
                    cursor.execute(f"DROP TABLE IF EXISTS {SUMMARY_COLLECTION}")

                # Create tables if they don't exist
                cursor.execute(f"""
                               CREATE TABLE IF NOT EXISTS {TOPICS_COLLECTION}
                               (
                                   name        TEXT PRIMARY KEY,
                                   description TEXT,
                                   item_count  INTEGER DEFAULT 0,
                                   created_at  TEXT NOT NULL,
                                   updated_at  TEXT NOT NULL
                               )
                               """)

                cursor.execute(f"""
                               CREATE TABLE IF NOT EXISTS {MEMORY_COLLECTION}
                               (
                                   id         TEXT PRIMARY KEY,
                                   content    TEXT NOT NULL,
                                   topic_name TEXT NOT NULL,
                                   tags       TEXT,
                                   created_at TEXT NOT NULL,
                                   updated_at TEXT NOT NULL,
                                   version    INTEGER DEFAULT 1,
                                   FOREIGN KEY (topic_name) REFERENCES {TOPICS_COLLECTION} (name) ON DELETE CASCADE
                               )
                               """)

                cursor.execute(f"""
                               CREATE TABLE IF NOT EXISTS {SUMMARY_COLLECTION}
                               (
                                   id           TEXT PRIMARY KEY,
                                   memory_id    TEXT NOT NULL,
                                   summary_type TEXT NOT NULL,
                                   summary_text TEXT NOT NULL,
                                   created_at   TEXT NOT NULL,
                                   updated_at   TEXT NOT NULL,
                                   FOREIGN KEY (memory_id) REFERENCES {MEMORY_COLLECTION} (id) ON DELETE CASCADE
                               )
                               """)

                conn.commit()
                return True

        except Exception as e:
            print(f"Error initializing SQLite database: {e}")
            return False

    def store_memory(self, memory_id: str, content: str, topic: str, tags: List[str]) -> bool:
        """Store a memory item in the database.
        
        Args:
            memory_id: Unique ID for the memory item
            content: The content to store
            topic: The topic category
            tags: List of tags
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()

                # Check if topic exists, create if not
                self._add_to_topic(topic, conn)

                # Store the memory item
                cursor.execute(
                    f"""
                    INSERT INTO {MEMORY_COLLECTION}
                        (id, content, topic_name, tags, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (memory_id, content, topic, ",".join(tags), now, now)
                )

                conn.commit()
                return True

        except Exception as e:
            print(f"Error storing memory in SQLite: {e}")
            return False

    def _add_to_topic(self, topic: str, conn: any) -> bool:
        try:
            now = timestamp()
            cursor = conn.cursor()

            # Check if topic exists, create if not
            cursor.execute(f"SELECT * FROM {TOPICS_COLLECTION} WHERE name = ?", (topic,))
            topic_exists = cursor.fetchone()

            if not topic_exists:
                cursor.execute(
                    f"INSERT INTO {TOPICS_COLLECTION} (name, item_count, created_at, updated_at ) VALUES (?, ?, ?, ?)",
                    (topic, 1, now, now)
                )
            else:
                cursor.execute(
                    f"""UPDATE {TOPICS_COLLECTION}
                       SET item_count = item_count + 1,
                           updated_at = ?
                       WHERE name = ?""",
                    (now, topic)
                )

            conn.commit()
            return True
        except Exception as e:
            print(f"Error storing memory in SQLite: {e}")
            return False

    def _remove_from_topic(self, topic: str, conn: any) -> bool:
        try:
            now = timestamp()
            cursor = conn.cursor()

            # Check if topic exists, create if not
            cursor.execute(f"SELECT * FROM {TOPICS_COLLECTION} WHERE name = ?", (topic,))
            current_topic = cursor.fetchone()

            if current_topic:
                # Only decrement if count > 1
                if current_topic["item_count"] > 1:
                    cursor.execute(
                        f"""UPDATE {TOPICS_COLLECTION}
                           SET item_count = item_count + 1,
                               updated_at = ?
                           WHERE name = ?""",
                        (now, topic)
                    )
                else:
                    # If count is 1, delete the topic
                    cursor.execute(f"DELETE FROM {TOPICS_COLLECTION} WHERE name = ?", (topic,))

            conn.commit()
            return True
        except Exception as e:
            print(f"Error storing memory in SQLite: {e}")
            return False

    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory item by ID.
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: The memory item or None if not found
        """
        try:
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {MEMORY_COLLECTION} WHERE id = ?", (memory_id,))
                item = cursor.fetchone()

                if not item:
                    return None

                return {
                    "id": item["id"],
                    "content": item["content"],
                    "topic_name": item["topic_name"],
                    "tags": item["tags"].split(",") if item["tags"] else [],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"],
                    "version": item["version"]
                }

        except Exception as e:
            print(f"Error getting memory from SQLite: {e}")
            return None

    def update_memory(self, memory_id: str,
                      content: Optional[str] = None,
                      topic: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> bool:
        """Update a memory item.
        
        Args:
            memory_id: The ID of the memory to update
            content: New content (if updating)
            topic: New topic (if updating)
            tags: New tags (if updating)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()

                # Get current item
                cursor.execute(f"SELECT * FROM {MEMORY_COLLECTION} WHERE id = ?", (memory_id,))
                current_item = cursor.fetchone()

                if not current_item:
                    return False

                # Prepare updated values
                new_content = content if content is not None else current_item["content"]
                new_topic = topic if topic is not None else current_item["topic_name"]
                new_tags = ",".join(tags) if tags is not None else current_item["tags"]

                # Update topic counts if topic is changing
                if topic is not None and topic != current_item["topic_name"]:
                    # Decrement old topic count
                    self._remove_from_topic(current_item["topic_name"], conn)

                    # Check if new topic exists, create if not
                    self._add_to_topic(topic, conn)

                # Update SQLite record
                cursor.execute(
                    f"""
                    UPDATE {MEMORY_COLLECTION}
                    SET content    = ?,
                        topic_name = ?,
                        tags       = ?,
                        updated_at = ?,
                        version    = version + 1
                    WHERE id = ?
                    """,
                    (new_content, new_topic, new_tags, now, memory_id)
                )

                conn.commit()
                return True

        except Exception as e:
            print(f"Error updating memory in SQLite: {e}")
            return False

    def list_topics(self) -> List[Dict[str, Any]]:
        """List all topics in the database.
        
        Returns:
            List[Dict[str, Any]]: List of topics
        """
        try:
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {TOPICS_COLLECTION} ORDER BY updated_at DESC")

                result = []
                for topic in cursor.fetchall():
                    result.append({
                        "name": topic["name"],
                        "description": topic["description"],
                        "item_count": topic["item_count"],
                        "created_at": topic["created_at"],
                        "updated_at": topic["updated_at"]
                    })

                return result

        except Exception as e:
            print(f"Error listing topics from SQLite: {e}")
            return []

    def get_status(self) -> Dict[str, Any]:
        """Get database status and statistics.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        try:
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()

                # Get memory items count
                cursor.execute(f"SELECT COUNT(*) as count FROM {MEMORY_COLLECTION}")
                memory_count = cursor.fetchone()["count"]

                # Get topics count
                cursor.execute(f"SELECT COUNT(*) as count FROM {TOPICS_COLLECTION}")
                topics_count = cursor.fetchone()["count"]

                # Get top topics
                cursor.execute(f"SELECT name, item_count FROM {TOPICS_COLLECTION} ORDER BY item_count DESC LIMIT 5")
                top_topics = cursor.fetchall()

                # Get latest item
                cursor.execute(f"SELECT created_at FROM {MEMORY_COLLECTION} ORDER BY created_at DESC LIMIT 1")
                latest_item = cursor.fetchone()

                return {
                    "total_memories": memory_count,
                    "total_topics": topics_count,
                    "top_topics": [{"name": t["name"], "count": t["item_count"]} for t in top_topics],
                    "latest_item_date": latest_item["created_at"] if latest_item else None
                }

        except Exception as e:
            print(f"Error getting status from SQLite: {e}")
            return {}

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item from the database.

        Args:
            memory_id: The ID of the memory to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()

                # Get the topic of the memory item before deleting
                cursor.execute(f"SELECT topic_name FROM {MEMORY_COLLECTION} WHERE id = ?", (memory_id,))
                topic_item = cursor.fetchone()

                if not topic_item:
                    return False  # Memory item not found

                topic = topic_item["topic_name"]

                # Delete the memory item
                cursor.execute(f"DELETE FROM {MEMORY_COLLECTION} WHERE id = ?", (memory_id,))

                # Decrement the item_count for the associated topic
                self._remove_from_topic(topic, conn)

                conn.commit()
                return True

        except Exception as e:
            print(f"Error deleting memory from SQLite: {e}")
            return False

    def store_summary(self, summary_id: str, memory_id: str, summary_type: str, summary_text: str) -> bool:
        """Store a summary item in the database.

        Args:
            summary_id: Unique ID for the summary item
            memory_id: The ID of the memory item this summary belongs to
            summary_type: The type of summary (e.g., 'abstractive_medium')
            summary_text: The summary content

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    f"""
                    INSERT INTO {SUMMARY_COLLECTION}
                        (id, memory_id, summary_type, summary_text, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (summary_id, memory_id, summary_type, summary_text, now, now)
                )

                conn.commit()
                return True

        except Exception as e:
            print(f"Error storing summary in SQLite: {e}")
            return False

    def list_summary_types_by_memory_id(self, memory_id: str, ) -> List[Dict[str, Any]]:
        """List all summaries of this memory in the database.

        Returns:
            List[Dict[str, Any]]: List of summary types and their counts
        """
        try:
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()
                summaries = cursor.execute(
                    f"SELECT summary_type, count(id) AS id_count FROM {SUMMARY_COLLECTION} WHERE memory_id = ? GROUP BY summary_type ORDER BY id_count DESC",
                    (memory_id,))

                result = []
                for item in cursor.fetchall():
                    result.append({
                        "summary_type": item["summary_type"],
                        "count": item["id_count"]
                    })
                return result

        except Exception as e:
            print(f"Error listing topics from SQLite: {e}")
            return []

    def get_summary(self, memory_id: str, summary_type: str) -> Optional[Dict[str, Any]]:
        """Get a summary item by memory ID and summary type.

        Args:
            memory_id: The ID of the memory to retrieve summary for
            summary_type: The type of summary to retrieve

        Returns:
            Optional[Dict[str, Any]]: The summary item or None if not found
        """
        try:
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT * FROM {SUMMARY_COLLECTION} WHERE memory_id = ? AND summary_type = ?",
                    (memory_id, summary_type)
                )
                item = cursor.fetchone()

                if not item:
                    return None

                return {
                    "id": item["id"],
                    "memory_id": item["memory_id"],
                    "summary_type": item["summary_type"],
                    "summary_text": item["summary_text"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"]
                }

        except Exception as e:
            print(f"Error getting summary from SQLite: {e}")
            return None

    def get_summary_by_id(self, summary_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary item by its unique ID.

        Args:
            summary_id: The unique ID of the summary to retrieve

        Returns:
            Optional[Dict[str, Any]]: The summary item or None if not found
        """
        try:
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"SELECT * FROM {SUMMARY_COLLECTION} WHERE id = ?",
                    (summary_id,)
                )
                item = cursor.fetchone()

                if not item:
                    return None

                return {
                    "id": item["id"],
                    "memory_id": item["memory_id"],
                    "summary_type": item["summary_type"],
                    "summary_text": item["summary_text"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"]
                }

        except Exception as e:
            print(f"Error getting summary by ID from SQLite: {e}")
            return None

    def update_summary(self, summary_id: str, new_summary_text: str) -> bool:
        """Update an existing summary item.

        Args:
            summary_id: The ID of the summary to update
            new_summary_text: The new summary content

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            now = timestamp()
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    f"""
                    UPDATE {SUMMARY_COLLECTION}
                    SET summary_text = ?,
                        updated_at   = ?
                    WHERE id = ?
                    """,
                    (new_summary_text, now, summary_id)
                )

                conn.commit()
                return True

        except Exception as e:
            print(f"Error updating summary in SQLite: {e}")
            return False

    def delete_summaries(self, memory_id: str) -> bool:
        """Delete all summaries associated with a memory ID.

        Args:
            memory_id: The ID of the memory whose summaries to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with SQLiteConnection(SQLITE_PATH) as conn:
                cursor = conn.cursor()

                cursor.execute(f"DELETE FROM {SUMMARY_COLLECTION} WHERE memory_id = ?", (memory_id,))

                conn.commit()
                return True

        except Exception as e:
            print(f"Error deleting summaries from SQLite: {e}")
            return False
