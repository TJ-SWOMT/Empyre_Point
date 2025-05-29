import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
from services.s3_service import S3Service

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
        self.s3_service = S3Service()

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
                                   'title', s.title,
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
                    background_image_url: Optional[str] = None,
                    title: str = '') -> Dict[str, Any]:
        """
        Create a new slide in a presentation.
        
        Args:
            presentation_id: The UUID of the presentation to add the slide to
            slide_number: The position of the slide in the presentation
            background_color: The background color of the slide (hex code)
            background_image_url: Optional URL for the slide's background image
            title: Optional title for the slide
            
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
                        INSERT INTO slides (presentation_id, slide_number, background_color, background_image_url, title)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING slide_id, presentation_id, slide_number, background_color, 
                                background_image_url, title, created_at, updated_at
                    """, (presentation_id, next_number, background_color, background_image_url, title))
                    
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
                    background_image_url: Optional[str] = None,
                    title: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a slide's properties.
        
        Args:
            slide_id: The UUID of the slide to update
            slide_number: New position in the presentation (optional)
            background_color: New background color (optional)
            background_image_url: New background image URL (optional)
            title: New title for the slide (optional)
            
        Returns:
            Dict containing updated slide information or None if not found
        """
        try:
            if not any([slide_number is not None, background_color, background_image_url, title is not None]):
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
            if title is not None:
                update_fields.append("title = %s")
                params.append(title)
            
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
                                background_image_url, title, created_at, updated_at
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

    def create_text_element(self, slide_id: int, content: str, x_position: float, y_position: float,
                          width: Optional[float] = None, height: Optional[float] = None,
                          font_family: str = 'Arial', font_size: int = 18,
                          font_color: str = '#000000', bold: bool = False,
                          italic: bool = False, underline: bool = False,
                          text_align: str = 'left', z_index: int = 0) -> Dict[str, Any]:
        """
        Create a new text element on a slide.
        
        Args:
            slide_id: The ID of the slide to add the text element to
            content: The markdown content of the text
            x_position: X coordinate position on the slide
            y_position: Y coordinate position on the slide
            width: Optional width of the text element
            height: Optional height of the text element
            font_family: Font family for the text
            font_size: Font size in pixels
            font_color: Font color in hex format
            bold: Whether the text is bold
            italic: Whether the text is italic
            underline: Whether the text is underlined
            text_align: Text alignment (left, center, right)
            z_index: Layer order of the element
            
        Returns:
            Dict containing the created text element's information
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # First create the slide element
                    cur.execute("""
                        INSERT INTO slide_elements 
                        (slide_id, element_type, x_position, y_position, width, height, z_index)
                        VALUES (%s, 'text', %s, %s, %s, %s, %s)
                        RETURNING element_id
                    """, (slide_id, x_position, y_position, width, height, z_index))
                    
                    element = cur.fetchone()
                    if not element:
                        raise Exception("Failed to create slide element")
                    
                    # Then create the text element
                    cur.execute("""
                        INSERT INTO text_elements 
                        (element_id, content, font_family, font_size, font_color, 
                         bold, italic, underline, text_align)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING element_id, content, font_family, font_size, font_color,
                                bold, italic, underline, text_align
                    """, (element['element_id'], content, font_family, font_size, font_color,
                         bold, italic, underline, text_align))
                    
                    text_element = cur.fetchone()
                    conn.commit()
                    
                    # Combine the information
                    return {
                        **dict(text_element),
                        'x_position': x_position,
                        'y_position': y_position,
                        'width': width,
                        'height': height,
                        'z_index': z_index,
                        'element_type': 'text'
                    }
                    
        except Exception as e:
            raise Exception(f"Error creating text element: {str(e)}")

    def update_text_element(self, element_id: int, content: Optional[str] = None,
                          x_position: Optional[float] = None, y_position: Optional[float] = None,
                          width: Optional[float] = None, height: Optional[float] = None,
                          font_family: Optional[str] = None, font_size: Optional[int] = None,
                          font_color: Optional[str] = None, bold: Optional[bool] = None,
                          italic: Optional[bool] = None, underline: Optional[bool] = None,
                          text_align: Optional[str] = None, z_index: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Update a text element's properties.
        
        Args:
            element_id: The ID of the text element to update
            content: New markdown content (optional)
            x_position: New X coordinate (optional)
            y_position: New Y coordinate (optional)
            width: New width (optional)
            height: New height (optional)
            font_family: New font family (optional)
            font_size: New font size (optional)
            font_color: New font color (optional)
            bold: New bold state (optional)
            italic: New italic state (optional)
            underline: New underline state (optional)
            text_align: New text alignment (optional)
            z_index: New z-index (optional)
            
        Returns:
            Dict containing updated text element information or None if not found
        """
        try:
            if not any([content, x_position is not None, y_position is not None,
                       width is not None, height is not None, font_family, font_size,
                       font_color, bold is not None, italic is not None,
                       underline is not None, text_align, z_index is not None]):
                raise Exception("At least one field must be provided for update")
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current element data first
                    cur.execute("""
                        SELECT se.x_position, se.y_position, se.width, se.height, se.z_index,
                               te.content, te.font_family, te.font_size, te.font_color,
                               te.bold, te.italic, te.underline, te.text_align
                        FROM slide_elements se
                        LEFT JOIN text_elements te ON se.element_id = te.element_id
                        WHERE se.element_id = %s
                    """, (element_id,))
                    
                    current_data = cur.fetchone()
                    if not current_data:
                        return None
                    
                    # Update slide_elements table
                    slide_update_fields = []
                    slide_params = []
                    
                    if x_position is not None:
                        slide_update_fields.append("x_position = %s")
                        slide_params.append(x_position)
                    if y_position is not None:
                        slide_update_fields.append("y_position = %s")
                        slide_params.append(y_position)
                    if width is not None:
                        slide_update_fields.append("width = %s")
                        slide_params.append(width)
                    if height is not None:
                        slide_update_fields.append("height = %s")
                        slide_params.append(height)
                    if z_index is not None:
                        slide_update_fields.append("z_index = %s")
                        slide_params.append(z_index)
                    
                    if slide_update_fields:
                        slide_update_fields.append("updated_at = NOW()")
                        slide_params.append(element_id)
                        
                        cur.execute(f"""
                            UPDATE slide_elements 
                            SET {', '.join(slide_update_fields)}
                            WHERE element_id = %s
                            RETURNING x_position, y_position, width, height, z_index
                        """, slide_params)
                        
                        updated_slide = cur.fetchone()
                        if not updated_slide:
                            return None
                    else:
                        updated_slide = {
                            'x_position': current_data['x_position'],
                            'y_position': current_data['y_position'],
                            'width': current_data['width'],
                            'height': current_data['height'],
                            'z_index': current_data['z_index']
                        }
                    
                    # Update text_elements table
                    text_update_fields = []
                    text_params = []
                    
                    if content is not None:
                        text_update_fields.append("content = %s")
                        text_params.append(content)
                    if font_family is not None:
                        text_update_fields.append("font_family = %s")
                        text_params.append(font_family)
                    if font_size is not None:
                        text_update_fields.append("font_size = %s")
                        text_params.append(font_size)
                    if font_color is not None:
                        text_update_fields.append("font_color = %s")
                        text_params.append(font_color)
                    if bold is not None:
                        text_update_fields.append("bold = %s")
                        text_params.append(bold)
                    if italic is not None:
                        text_update_fields.append("italic = %s")
                        text_params.append(italic)
                    if underline is not None:
                        text_update_fields.append("underline = %s")
                        text_params.append(underline)
                    if text_align is not None:
                        text_update_fields.append("text_align = %s")
                        text_params.append(text_align)
                    
                    if text_update_fields:
                        text_params.append(element_id)
                        
                        cur.execute(f"""
                            UPDATE text_elements 
                            SET {', '.join(text_update_fields)}
                            WHERE element_id = %s
                            RETURNING content, font_family, font_size, font_color,
                                    bold, italic, underline, text_align
                        """, text_params)
                        
                        updated_text = cur.fetchone()
                        if not updated_text:
                            return None
                    else:
                        updated_text = {
                            'content': current_data['content'],
                            'font_family': current_data['font_family'],
                            'font_size': current_data['font_size'],
                            'font_color': current_data['font_color'],
                            'bold': current_data['bold'],
                            'italic': current_data['italic'],
                            'underline': current_data['underline'],
                            'text_align': current_data['text_align']
                        }
                    
                    conn.commit()
                    
                    # Combine the information
                    return {
                        'element_id': element_id,
                        'element_type': 'text',
                        **dict(updated_slide),
                        **dict(updated_text)
                    }
                    
        except Exception as e:
            raise Exception(f"Error updating text element: {str(e)}")

    def delete_element(self, element_id: int) -> bool:
        """
        Delete an element from a slide.
        
        Args:
            element_id: The ID of the element to delete
            
        Returns:
            True if deletion was successful, False if element not found
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # The deletion will cascade to the specific element table
                    cur.execute("""
                        DELETE FROM slide_elements
                        WHERE element_id = %s
                        RETURNING element_id
                    """, (element_id,))
                    
                    deleted = cur.fetchone()
                    conn.commit()
                    return bool(deleted)
                    
        except Exception as e:
            raise Exception(f"Error deleting element: {str(e)}")

    def get_slide_elements(self, slide_id: int) -> List[Dict[str, Any]]:
        """
        Get all elements for a slide.
        
        Args:
            slide_id: The ID of the slide to get elements for
            
        Returns:
            List of dictionaries containing element information
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            se.element_id,
                            se.element_type,
                            se.x_position,
                            se.y_position,
                            se.width,
                            se.height,
                            se.z_index,
                            CASE 
                                WHEN se.element_type = 'text' THEN 
                                    json_build_object(
                                        'content', te.content,
                                        'font_family', te.font_family,
                                        'font_size', te.font_size,
                                        'font_color', te.font_color,
                                        'bold', te.bold,
                                        'italic', te.italic,
                                        'underline', te.underline,
                                        'text_align', te.text_align
                                    )
                                WHEN se.element_type = 'image' THEN 
                                    json_build_object(
                                        'image_url', ie.image_url,
                                        'alt_text', ie.alt_text
                                    )
                                ELSE NULL
                            END as element_data
                        FROM slide_elements se
                        LEFT JOIN text_elements te ON se.element_id = te.element_id
                        LEFT JOIN image_elements ie ON se.element_id = ie.element_id
                        WHERE se.slide_id = %s
                        ORDER BY se.z_index
                    """, (slide_id,))
                    
                    elements = cur.fetchall()
                    return [{
                        **dict(element),
                        'element_data': element['element_data'] if element['element_data'] else {}
                    } for element in elements]
                    
        except Exception as e:
            raise Exception(f"Error retrieving slide elements: {str(e)}")

    def create_image_element(self, slide_id: int, image_url: str, x_position: float, y_position: float,
                           width: Optional[float] = None, height: Optional[float] = None,
                           alt_text: Optional[str] = None, z_index: int = 0) -> Dict[str, Any]:
        """
        Create a new image element on a slide.
        
        Args:
            slide_id: The ID of the slide to add the image element to
            image_url: The URL of the image
            x_position: X coordinate position on the slide
            y_position: Y coordinate position on the slide
            width: Optional width of the image element
            height: Optional height of the image element
            alt_text: Optional alt text for the image
            z_index: Layer order of the element
            
        Returns:
            Dict containing the created image element's information
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # First create the slide element
                    cur.execute("""
                        INSERT INTO slide_elements 
                        (slide_id, element_type, x_position, y_position, width, height, z_index)
                        VALUES (%s, 'image', %s, %s, %s, %s, %s)
                        RETURNING element_id
                    """, (slide_id, x_position, y_position, width, height, z_index))
                    
                    element = cur.fetchone()
                    if not element:
                        raise Exception("Failed to create slide element")
                    
                    # Then create the image element
                    cur.execute("""
                        INSERT INTO image_elements 
                        (element_id, image_url, alt_text)
                        VALUES (%s, %s, %s)
                        RETURNING element_id, image_url, alt_text
                    """, (element['element_id'], image_url, alt_text))
                    
                    image_element = cur.fetchone()
                    conn.commit()
                    
                    # Combine the information
                    return {
                        **dict(image_element),
                        'x_position': x_position,
                        'y_position': y_position,
                        'width': width,
                        'height': height,
                        'z_index': z_index,
                        'element_type': 'image'
                    }
                    
        except Exception as e:
            raise Exception(f"Error creating image element: {str(e)}")

    def update_image_element(self, element_id: int, image_url: Optional[str] = None,
                           x_position: Optional[float] = None, y_position: Optional[float] = None,
                           width: Optional[float] = None, height: Optional[float] = None,
                           alt_text: Optional[str] = None, z_index: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Update an image element's properties.
        
        Args:
            element_id: The ID of the image element to update
            image_url: New image URL (optional)
            x_position: New X coordinate (optional)
            y_position: New Y coordinate (optional)
            width: New width (optional)
            height: New height (optional)
            alt_text: New alt text (optional)
            z_index: New z-index (optional)
            
        Returns:
            Dict containing updated image element information or None if not found
        """
        try:
            if not any([image_url, x_position is not None, y_position is not None,
                       width is not None, height is not None, alt_text, z_index is not None]):
                raise Exception("At least one field must be provided for update")
            
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    # Get current element data first
                    cur.execute("""
                        SELECT se.x_position, se.y_position, se.width, se.height, se.z_index,
                               ie.image_url, ie.alt_text
                        FROM slide_elements se
                        LEFT JOIN image_elements ie ON se.element_id = ie.element_id
                        WHERE se.element_id = %s
                    """, (element_id,))
                    
                    current_data = cur.fetchone()
                    if not current_data:
                        return None
                    
                    # Update slide_elements table
                    slide_update_fields = []
                    slide_params = []
                    
                    if x_position is not None:
                        slide_update_fields.append("x_position = %s")
                        slide_params.append(x_position)
                    if y_position is not None:
                        slide_update_fields.append("y_position = %s")
                        slide_params.append(y_position)
                    if width is not None:
                        slide_update_fields.append("width = %s")
                        slide_params.append(width)
                    if height is not None:
                        slide_update_fields.append("height = %s")
                        slide_params.append(height)
                    if z_index is not None:
                        slide_update_fields.append("z_index = %s")
                        slide_params.append(z_index)
                    
                    if slide_update_fields:
                        slide_update_fields.append("updated_at = NOW()")
                        slide_params.append(element_id)
                        
                        cur.execute(f"""
                            UPDATE slide_elements 
                            SET {', '.join(slide_update_fields)}
                            WHERE element_id = %s
                            RETURNING x_position, y_position, width, height, z_index
                        """, slide_params)
                        
                        updated_slide = cur.fetchone()
                        if not updated_slide:
                            return None
                    else:
                        updated_slide = {
                            'x_position': current_data['x_position'],
                            'y_position': current_data['y_position'],
                            'width': current_data['width'],
                            'height': current_data['height'],
                            'z_index': current_data['z_index']
                        }
                    
                    # Update image_elements table
                    image_update_fields = []
                    image_params = []
                    
                    if image_url is not None:
                        # Delete old image from S3 if URL is changing
                        if current_data['image_url'] != image_url:
                            self.s3_service.delete_image(current_data['image_url'])
                        image_update_fields.append("image_url = %s")
                        image_params.append(image_url)
                    if alt_text is not None:
                        image_update_fields.append("alt_text = %s")
                        image_params.append(alt_text)
                    
                    if image_update_fields:
                        image_params.append(element_id)
                        
                        cur.execute(f"""
                            UPDATE image_elements 
                            SET {', '.join(image_update_fields)}
                            WHERE element_id = %s
                            RETURNING image_url, alt_text
                        """, image_params)
                        
                        updated_image = cur.fetchone()
                        if not updated_image:
                            return None
                    else:
                        updated_image = {
                            'image_url': current_data['image_url'],
                            'alt_text': current_data['alt_text']
                        }
                    
                    conn.commit()
                    
                    # Combine the information
                    return {
                        'element_id': element_id,
                        'element_type': 'image',
                        **dict(updated_slide),
                        **dict(updated_image)
                    }
                    
        except Exception as e:
            raise Exception(f"Error updating image element: {str(e)}") 