import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class PresentationsService:
    def __init__(self):
        """Initialize the service with database connection parameters."""
        self.db_params = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USERNAME'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_ENDPOINT'),
            'port': os.getenv('DB_PORT')
        }

    def _get_connection(self):
        """Create and return a database connection."""
        return psycopg2.connect(**self.db_params, cursor_factory=RealDictCursor)

    def create_presentation(self, user_id: int, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new presentation for a user.
        
        Args:
            user_id: The ID of the user creating the presentation
            title: The title of the presentation
            description: Optional description of the presentation
            
        Returns:
            Dict containing the created presentation's information
            
        Raises:
            Exception: If presentation creation fails
        """
        try:
            if not user_id or not title:
                raise Exception("User ID and title are required")
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO presentations (user_id, title, description)
                        VALUES (%s, %s, %s)
                        RETURNING presentation_id, user_id, title, description, created_at, updated_at
                    """, (user_id, title, description))
                    
                    presentation = cur.fetchone()
                    conn.commit()
                    return dict(presentation)
                    
        except Exception as e:
            raise Exception(f"Error creating presentation: {str(e)}")

    def get_presentation(self, presentation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a presentation by its ID.
        
        Args:
            presentation_id: The UUID of the presentation to retrieve
            
        Returns:
            Dict containing presentation information or None if not found
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.*, 
                               json_agg(json_build_object(
                                   'slide_id', s.slide_id,
                                   'slide_number', s.slide_number,
                                   'background_color', s.background_color,
                                   'background_image_url', s.background_image_url,
                                   'created_at', s.created_at,
                                   'updated_at', s.updated_at
                               ) ORDER BY s.slide_number) as slides
                        FROM presentations p
                        LEFT JOIN slides s ON p.presentation_id = s.presentation_id
                        WHERE p.presentation_id = %s
                        GROUP BY p.presentation_id
                    """, (presentation_id,))
                    
                    presentation = cur.fetchone()
                    if presentation and presentation['slides'][0] is None:
                        presentation['slides'] = []
                    return dict(presentation) if presentation else None
                    
        except Exception as e:
            raise Exception(f"Error retrieving presentation: {str(e)}")

    def get_user_presentations(self, user_id: int) -> List[Dict[str, Any]]:
        print("get_user_presentations!!!!11111")
        print("user_id", user_id)
        """
        Retrieve all presentations for a user.
        
        Args:
            user_id: The ID of the user whose presentations to retrieve
            
        Returns:
            List of dictionaries containing presentation information
        """
        print("get_user_presentations!!!!22222")
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.*, 
                               COUNT(s.slide_id) as slide_count,
                               MAX(s.updated_at) as last_updated
                        FROM presentations p
                        LEFT JOIN slides s ON p.presentation_id = s.presentation_id
                        WHERE p.user_id = %s
                        GROUP BY p.presentation_id
                        ORDER BY p.updated_at DESC
                    """, (user_id,))
                    
                    presentations = cur.fetchall()
                    return [dict(p) for p in presentations]
                    
        except Exception as e:
            raise Exception(f"Error retrieving user presentations: {str(e)}")

    def update_presentation(self, presentation_id: str, title: Optional[str] = None, 
                          description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a presentation's title and/or description.
        
        Args:
            presentation_id: The UUID of the presentation to update
            title: New title (optional)
            description: New description (optional)
            
        Returns:
            Dict containing updated presentation information or None if not found
        """
        try:
            if not title and not description:
                raise Exception("At least one field (title or description) must be provided")
            
            update_fields = []
            params = []
            if title:
                update_fields.append("title = %s")
                params.append(title)
            if description:
                update_fields.append("description = %s")
                params.append(description)
            
            update_fields.append("updated_at = NOW()")
            params.append(presentation_id)
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        UPDATE presentations 
                        SET {', '.join(update_fields)}
                        WHERE presentation_id = %s
                        RETURNING presentation_id, user_id, title, description, created_at, updated_at
                    """, params)
                    
                    presentation = cur.fetchone()
                    conn.commit()
                    return dict(presentation) if presentation else None
                    
        except Exception as e:
            raise Exception(f"Error updating presentation: {str(e)}")

    def delete_presentation(self, presentation_id: str) -> bool:
        """
        Delete a presentation and all its slides.
        
        Args:
            presentation_id: The UUID of the presentation to delete
            
        Returns:
            True if deletion was successful, False if presentation not found
            
        Note:
            This will cascade delete all slides and their elements due to foreign key constraints
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM presentations
                        WHERE presentation_id = %s
                        RETURNING presentation_id
                    """, (presentation_id,))
                    
                    deleted = cur.fetchone()
                    conn.commit()
                    return bool(deleted)
                    
        except Exception as e:
            raise Exception(f"Error deleting presentation: {str(e)}")

    def create_slide(self, presentation_id: str, slide_number: int, 
                    background_color: str = '#FFFFFF', 
                    background_image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new slide in a presentation.
        
        Args:
            presentation_id: The UUID of the presentation to add the slide to
            slide_number: The position of the slide in the presentation
            background_color: The background color of the slide (hex code)
            background_image_url: Optional URL for the slide's background image
            
        Returns:
            Dict containing the created slide's information
            
        Raises:
            Exception: If slide creation fails
        """
        try:
            if not presentation_id or slide_number is None:
                raise Exception("Presentation ID and slide number are required")
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Get the next available slide number
                    cur.execute("""
                        SELECT COALESCE(MAX(slide_number), 0) + 1 as next_number
                        FROM slides
                        WHERE presentation_id = %s
                    """, (presentation_id,))
                    result = cur.fetchone()
                    next_number = result['next_number']
                    
                    # Insert the new slide with the next available number
                    cur.execute("""
                        INSERT INTO slides (presentation_id, slide_number, background_color, background_image_url)
                        VALUES (%s, %s, %s, %s)
                        RETURNING slide_id, presentation_id, slide_number, background_color, 
                                background_image_url, created_at, updated_at
                    """, (presentation_id, next_number, background_color, background_image_url))
                    
                    slide = cur.fetchone()
                    conn.commit()
                    return dict(slide)
                    
        except psycopg2.IntegrityError as e:
            if "slides_presentation_id_slide_number_key" in str(e):
                raise Exception("Slide number already exists in this presentation")
            raise Exception("Failed to create slide")
        except Exception as e:
            raise Exception(f"Error creating slide: {str(e)}")

    def update_slide(self, slide_id: str, slide_number: Optional[int] = None,
                    background_color: Optional[str] = None,
                    background_image_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a slide's properties.
        
        Args:
            slide_id: The UUID of the slide to update
            slide_number: New position in the presentation (optional)
            background_color: New background color (optional)
            background_image_url: New background image URL (optional)
            
        Returns:
            Dict containing updated slide information or None if not found
        """
        try:
            if not any([slide_number is not None, background_color, background_image_url]):
                raise Exception("At least one field must be provided for update")
            
            update_fields = []
            params = []
            
            if slide_number is not None:
                update_fields.append("slide_number = %s")
                params.append(slide_number)
            if background_color:
                update_fields.append("background_color = %s")
                params.append(background_color)
            if background_image_url:
                update_fields.append("background_image_url = %s")
                params.append(background_image_url)
            
            update_fields.append("updated_at = NOW()")
            params.append(slide_id)
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # If updating slide number, we need to handle reordering
                    if slide_number is not None:
                        # Get the current slide number and presentation_id
                        cur.execute("""
                            SELECT slide_number, presentation_id
                            FROM slides
                            WHERE slide_id = %s
                        """, (slide_id,))
                        current = cur.fetchone()
                        if not current:
                            return None
                            
                        # Update other slides to make room for the new position
                        if current['slide_number'] < slide_number:
                            cur.execute("""
                                UPDATE slides
                                SET slide_number = slide_number - 1
                                WHERE presentation_id = %s 
                                AND slide_number > %s 
                                AND slide_number <= %s
                            """, (current['presentation_id'], current['slide_number'], slide_number))
                        elif current['slide_number'] > slide_number:
                            cur.execute("""
                                UPDATE slides
                                SET slide_number = slide_number + 1
                                WHERE presentation_id = %s 
                                AND slide_number >= %s 
                                AND slide_number < %s
                            """, (current['presentation_id'], slide_number, current['slide_number']))
                    
                    # Update the slide
                    cur.execute(f"""
                        UPDATE slides 
                        SET {', '.join(update_fields)}
                        WHERE slide_id = %s
                        RETURNING slide_id, presentation_id, slide_number, background_color, 
                                background_image_url, created_at, updated_at
                    """, params)
                    
                    slide = cur.fetchone()
                    conn.commit()
                    return dict(slide) if slide else None
                    
        except Exception as e:
            raise Exception(f"Error updating slide: {str(e)}")

    def delete_slide(self, slide_id: str) -> bool:
        """
        Delete a slide and reorder remaining slides.
        
        Args:
            slide_id: The UUID of the slide to delete
            
        Returns:
            True if deletion was successful, False if slide not found
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Get the slide's position and presentation_id before deleting
                    cur.execute("""
                        SELECT slide_number, presentation_id
                        FROM slides
                        WHERE slide_id = %s
                    """, (slide_id,))
                    slide_info = cur.fetchone()
                    if not slide_info:
                        return False
                    
                    # Delete the slide
                    cur.execute("""
                        DELETE FROM slides
                        WHERE slide_id = %s
                    """, (slide_id,))
                    
                    # Reorder remaining slides
                    cur.execute("""
                        UPDATE slides
                        SET slide_number = slide_number - 1
                        WHERE presentation_id = %s AND slide_number > %s
                    """, (slide_info['presentation_id'], slide_info['slide_number']))
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            raise Exception(f"Error deleting slide: {str(e)}") 