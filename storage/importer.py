import pandas as pd
from typing import List, Tuple
from models.post import SocialPost
from models.enums import Platform, Tone, PostStatus
from storage.local import save_post
from datetime import datetime
import io

def import_csv_calendar(file_content: bytes) -> Tuple[int, List[str]]:
    """
    Parses an uploaded CSV file and saves the posts.
    Returns the number of successfully imported posts and a list of error messages.
    """
    errors = []
    success_count = 0
    
    try:
        # Read the file content as CSV
        df = pd.read_csv(io.BytesIO(file_content))
        
        required_columns = ["content", "platform"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return 0, errors
            
        for index, row in df.iterrows():
            try:
                content = str(row["content"])
                platform_str = str(row["platform"])
                tone_str = str(row.get("tone", Tone.PROFESSIONAL.value))
                scheduled_time_str = str(row.get("scheduled_time", ""))
                
                # Validate enum values
                try:
                    platform = Platform(platform_str)
                except ValueError:
                    errors.append(f"Row {index + 2}: Invalid platform '{platform_str}'")
                    continue
                    
                try:
                    tone = Tone(tone_str)
                except ValueError:
                    tone = Tone.PROFESSIONAL # Default fallback
                
                # Parse datetime if provided
                scheduled_time = None
                if scheduled_time_str and scheduled_time_str.lower() != "nan":
                    try:
                        scheduled_time = datetime.fromisoformat(scheduled_time_str)
                    except ValueError:
                        errors.append(f"Row {index + 2}: Invalid scheduled_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
                        continue
                
                post = SocialPost(
                    content=content,
                    platform=platform,
                    tone=tone,
                    status=PostStatus.SCHEDULED if scheduled_time else PostStatus.DRAFT,
                    scheduled_time=scheduled_time
                )
                
                save_post(post)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: Unexpected error - {str(e)}")
                
    except Exception as e:
        errors.append(f"Failed to read CSV file: {str(e)}")
        
    return success_count, errors
